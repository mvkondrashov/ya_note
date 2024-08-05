from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Mr Logic')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

        cls.note = Note.objects.create(
            title='Title',
            text='Text',
            author=cls.user,
            slug='note1',
        )
        cls.url = reverse('notes:add')

        cls.form_data = {
            'title': 'New title',
            'text': 'New text',
            'slug': 'newslug',
        }

    def test_anonymous_cannot_create_note(self):
        """
        Test notes number after anonymous user
        send post-request to add new note
        """
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_user_can_create_note(self):
        """
        Test notes number after authorized user
        send post-request to add new note
        """
        self.auth_client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)

        newnote = Note.objects.last()
        self.assertEqual(newnote.text, 'New text')
        self.assertEqual(newnote.author, self.user)

    def test_user_cannot_use_existing_slug(self):
        """Test note creation with existing slug"""
        existing_slug = {
            'title': 'Title',
            'text': 'Text',
            'slug': 'note1',
        }
        response = self.auth_client.post(self.url, data=existing_slug)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=existing_slug['slug'] + WARNING
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)


class TestNoteEditDelete(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.NOTE_TEXT = "Don't be afraid to fail. Be afraid not to try."
        cls.NEW_NOTE_TEXT = 'The harder I prepare, the luckier I seem to get.'

        cls.author = User.objects.create(username='M Jordan')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='S Pippen')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title='Note 23',
            text=cls.NOTE_TEXT,
            author=cls.author,
            slug='note23',
        )

        cls.form_data = {
            'title': 'Note23',
            'text': cls.NEW_NOTE_TEXT,
        }

        cls.success_url = reverse('notes:success')
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_author_can_delete_note(self):
        """Test author can delete his own note"""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        """Number of notes reduced"""
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cannot_delete_note_of_another_user(self):
        """Test authorized user cannot delete note of another user"""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        """Number of notes remained the same"""
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        """Test author can edit his own note"""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        """Check the note text updated"""
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cannot_edit_note_of_another_user(self):
        """Test authorized user cannot edit note of another user"""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        """Check the note text not updated"""
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
