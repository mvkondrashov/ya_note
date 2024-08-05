from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestForm(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author A')
        cls.note = Note.objects.create(
            title='Title',
            text='Text',
            author=cls.author,
            slug='note1',
        )

    def test_authorized_user_has_form(self):
        """Test form availability for authorized user"""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        for name, args in urls:
            url = reverse(name, args=args)
            self.client.force_login(self.author)
            response = self.client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)


class TestListPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author A')
        cls.reader = User.objects.create(username='No O. Cares')
        data = (
            (cls.author, 'note1',),
            (cls.reader, 'note2',),
        )
        all_notes = [
            Note(title='Title', text=f'Text {user}', author=user, slug=slug)
            for user, slug in data
        ]
        Note.objects.bulk_create(all_notes)

    def test_authorized_user_sees_only_his_own_notes(self):
        """Test authorized user sees only his own notes"""
        url = reverse('notes:list')
        self.client.force_login(self.author)
        response = self.client.get(url)
        object_list = response.context['object_list']
        notes_count = object_list.count()
        self.assertEqual(notes_count, 1)
