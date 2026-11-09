"""Real Django/Cotton rendering, using the same files the CLI installs.

python -m pip install -r tests/cotton/requirements.txt
python -m unittest discover -s tests/cotton
"""
import json
import re
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

from django.conf import settings

ROOT = Path(__file__).resolve().parents[2]
COTTON = ROOT / 'registry' / 'django-cotton'
TEMPLATES = tempfile.TemporaryDirectory(prefix='shadcn-cotton-')
Path(TEMPLATES.name, 'cotton').symlink_to(COTTON, target_is_directory=True)
sys.path.insert(0, str(COTTON / '_lib'))
settings.configure(
    SECRET_KEY='render-tests',
    INSTALLED_APPS=['django_cotton'],
    TEMPLATES=[{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES.name],
        'APP_DIRS': True,
        'OPTIONS': {'libraries': {'shadcn_htmx': 'shadcn_htmx'}},
    }],
)
import django

django.setup()
from django.template import engines
from django.utils import translation
from django_cotton.compiler_regex import CottonCompiler

ENGINE = engines['django']
COMPILER = CottonCompiler()
MANIFEST = json.loads((ROOT / 'registry.json').read_text())
USAGES = json.loads((ROOT / 'app/data/cotton-usage.json').read_text())


def render(source, **context):
    return ENGINE.from_string(COMPILER.process(source)).render(context)


class Elements(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.elements = []
        self.duplicates = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        names = [name for name, _ in attrs]
        self.duplicates.extend((tag, name) for name in set(names) if names.count(name) > 1)
        self.elements.append((tag, dict(attrs)))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def one(self, tag=None, slot=None):
        return next(attrs for name, attrs in self.elements
                    if (tag is None or name == tag) and (slot is None or attrs.get('data-slot') == slot))


class CottonRenderingTests(unittest.TestCase):
    def test_every_family_is_installed_and_documented(self):
        items = [item for item in MANIFEST['items'] if item['type'] == 'registry:ui']
        self.assertEqual(len(items), 82)
        self.assertEqual(set(USAGES), {item['name'] for item in items})
        installed = set()
        for item in items:
            files = [f for f in item['files'] if f['path'].startswith('registry/django-cotton/')]
            self.assertTrue(files, item['name'])
            for file in files:
                self.assertTrue((ROOT / file['path']).is_file(), file['path'])
                installed.add(file['path'])
                if file['path'].endswith('.html'):
                    self.assertEqual(file['target'], file['path'].replace('registry/django-cotton/', 'templates/cotton/'))
        self.assertEqual(installed, {str(p.relative_to(ROOT)) for p in COTTON.rglob('*') if p.suffix in ('.html', '.py')})

    def test_every_template_compiles_and_renders(self):
        for path in sorted(COTTON.rglob('*.html')):
            tag = str(path.relative_to(COTTON)).removesuffix('.html').replace('/', '.').replace('_', '-').removesuffix('.index')
            with self.subTest(tag=tag):
                result = render(f'<c-{tag} />')
                self.assertNotIn('<c-', result)
                self.assertNotIn('{%', result)
                self.assertNotIn('{{', result)
                self.assertFalse(Elements(result).duplicates)

    def test_documented_examples_render_without_duplicate_attributes(self):
        for name, usage in USAGES.items():
            with self.subTest(component=name):
                result = render(usage, csrf_token='test-csrf')
                self.assertNotIn('<c-', result)
                self.assertFalse(Elements(result).duplicates)

    def test_button_variants_slots_and_attribute_escaping(self):
        result = render('''<c-button variant="outline" size="sm" class="custom" :disabled="False"
            :pressed="False" aria-label="Save" hx-post="/save/" :data-message="message">
            <strong>{{ label }}</strong>
        </c-button>''', message='" onmouseover="alert(1)', label='<script>bad</script>')
        elements = Elements(result)
        button = elements.one('button')
        self.assertIn('border', button['class'].split())
        self.assertIn('h-8', button['class'].split())
        self.assertIn('custom', button['class'].split())
        self.assertEqual(button['aria-pressed'], 'false')
        self.assertEqual(button['aria-label'], 'Save')
        self.assertEqual(button['hx-post'], '/save/')
        self.assertNotIn('disabled', button)
        self.assertNotIn('onmouseover', button)
        self.assertNotIn('<script>', result)
        self.assertIn('<strong>&lt;script&gt;', result)
        self.assertFalse(elements.duplicates)

    def test_native_boolean_attributes_and_numeric_zero(self):
        for tag in ('input', 'checkbox', 'switch', 'select', 'textarea'):
            with self.subTest(tag=tag):
                disabled = Elements(render(f'<c-{tag} disabled required :value="0" />'))
                control = next(attrs for name, attrs in disabled.elements if name in ('input', 'select', 'textarea'))
                self.assertIn('disabled', control)
                self.assertIn('required', control)
                enabled = Elements(render(f'<c-{tag} :disabled="False" :required="False" />'))
                control = next(attrs for name, attrs in enabled.elements if name in ('input', 'select', 'textarea'))
                self.assertNotIn('disabled', control)
                self.assertNotIn('required', control)
        self.assertEqual(Elements(render('<c-input :value="0" :min="0" />')).one('input')['value'], '0')

    def test_compound_slots_and_context_do_not_leak(self):
        result = render('''<c-card><c-card.header><c-card.title as="h2">Account</c-card.title></c-card.header>
          <c-card.content><c-button variant="destructive">Delete</c-button><c-button>Save</c-button></c-card.content></c-card>''')
        parsed = Elements(result)
        self.assertIn('<h2', result)
        buttons = [attrs for name, attrs in parsed.elements if name == 'button']
        self.assertEqual([b['data-variant'] for b in buttons], ['destructive', 'default'])
        self.assertIn('Account', result)
        self.assertFalse(parsed.duplicates)
        result = render('<c-container-card title="Walks"><c-slot name="media"><img alt="Coast" /></c-slot>Explore</c-container-card>')
        self.assertIn('<img alt="Coast"', result)
        self.assertNotIn('&lt;img', result)

    def test_native_dialog_and_valid_aria_references(self):
        result = render('''<c-dialog.trigger dialog-for="edit" native>Edit</c-dialog.trigger>
          <c-dialog id="edit" title="Edit profile"><c-dialog.close commandfor="edit">Done</c-dialog.close></c-dialog>''')
        parsed = Elements(result)
        self.assertEqual(parsed.one('button')['command'], 'show-modal')
        self.assertEqual(parsed.one('button')['commandfor'], 'edit')
        dialog = parsed.one('dialog')
        self.assertEqual(dialog['aria-labelledby'], 'edit-title')
        self.assertNotIn('aria-describedby', dialog)
        self.assertTrue(any(attrs.get('id') == 'edit-title' for _, attrs in parsed.elements))

    def test_htmx_overrides_are_not_duplicated(self):
        parsed = Elements(render('''<c-active-search id="q" action="/default/" hx-get="/custom/"
            hx-trigger="input changed delay:500ms" hx-sync="this:replace" hx-indicator="#busy" hx-target="#results" />'''))
        attrs = parsed.one('input')
        self.assertEqual(attrs['hx-get'], '/custom/')
        self.assertEqual(attrs['hx-trigger'], 'input changed delay:500ms')
        self.assertEqual(attrs['hx-target'], '#results')
        self.assertFalse(parsed.duplicates)

    def test_data_lists_and_escaping(self):
        result = render('<c-combobox id="city" :options="options" />', options=[{'value':'dk','label':'<Copenhagen>'}])
        self.assertEqual(Elements(result).one('option')['value'], 'dk')
        self.assertIn('&lt;Copenhagen&gt;', result)
        result = render('<c-theme-toggle value="dark" />')
        self.assertEqual(sum('checked' in attrs for tag, attrs in Elements(result).elements if tag=='input'), 1)

    def test_progress_range_rating_and_localization(self):
        with translation.override('da'):
            result = render('<c-progress :value="25" :min="0" :max="200" />')
            attrs = Elements(result).one(slot='progress-indicator')
            self.assertEqual(attrs['style'], 'width: 12.5%')
            result = render('<c-input type="number" :value="price" />', price=12.5)
            self.assertEqual(Elements(result).one('input')['value'], '12.5')
        result = render('<c-progress />')
        self.assertNotIn('aria-valuenow', Elements(result).one(slot='progress'))
        result = render('<c-progress :value="500" />')
        self.assertEqual(float(Elements(result).one(slot='progress')['aria-valuenow']), 100)
        result = render('<c-range-slider :min-value="20" :max-value="80" />')
        attrs = Elements(result).one(slot='range-slider')
        self.assertIn('--range-min:20.0%', attrs['style'])
        self.assertIn('--range-max:80.0%', attrs['style'])
        result = render('<c-rating name="score" :max="7" :value="3" />')
        radios = [attrs for tag,attrs in Elements(result).elements if tag=='input']
        self.assertEqual(len(radios), 7)
        self.assertEqual([a['value'] for a in radios if 'checked' in a], ['3'])

    def test_highlight_does_not_trust_input_as_html_or_regex(self):
        result = render('<c-highlight :text="text" :query="query" />', text='<script>A+B a+b</script>', query='a+b')
        self.assertNotIn('<script>', result)
        self.assertIn('&lt;script&gt;', result)
        self.assertEqual(sum(tag=='mark' for tag,_ in Elements(result).elements), 2)
        self.assertIn('A+B</mark>', result)
        result = render('<c-highlight text="Django and HTMX" query="Django HTMX" words />')
        self.assertEqual(sum(tag=='mark' for tag,_ in Elements(result).elements), 2)

    def test_named_optimistic_slot(self):
        result = render('<c-optimistic-toggle id="like" :pressed="False">Like<c-slot name="optimistic">Liked</c-slot></c-optimistic-toggle>')
        self.assertEqual(Elements(result).one('button')['aria-pressed'], 'false')
        template = result.split('<template', 1)[1].split('</template>', 1)[0]
        self.assertIn('>Liked</span>', template)
        self.assertEqual(Elements(result).one(slot='optimistic-toggle-state')['aria-pressed'], 'true')

    def test_form_errors_reference_rendered_descriptions(self):
        result = render('<c-form-field.fieldset id="plan" legend="Plan" description="Choose one" error="Required">Controls</c-form-field.fieldset>')
        attrs = Elements(result).one('fieldset')
        self.assertEqual(attrs['aria-describedby'].split(), ['plan-description','plan-error'])
        self.assertEqual(attrs['aria-invalid'], 'true')

    def test_tree_boolean_states_are_valid_aria_tokens(self):
        result = render('<c-tree.item label="Notes" :expanded="False" :selected="True" :current="True" />')
        attrs = Elements(result).one('li')
        self.assertEqual(attrs['aria-expanded'], 'false')
        self.assertEqual(attrs['aria-selected'], 'true')
        self.assertEqual(attrs['aria-current'], 'page')


if __name__ == '__main__':
    unittest.main()
