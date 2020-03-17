from django.test import TestCase
from django.urls import resolve
from lists.views import home_page
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.html import escape
from unittest import skip
from unittest.mock import patch, Mock

from lists.models import Item, List
from lists.forms import (
    ItemForm, ExistingListItemForm,
    EMPTY_ITEM_ERROR, DUPLICATE_ITEM_ERROR,
)
from lists.views import new_list

from django.contrib.auth import get_user_model
User = get_user_model()

# Create your tests here.
class HomePageTest(TestCase):

    def test_uses_home_templates(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')
        # self.assertEqual(response['location'], '/')

    def test_home_page_uses_item_form(self):
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], ItemForm)


class ListViewTest(TestCase):
    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertTemplateUsed(response, 'list.html')

    def test_passes_correct_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.get(f'/lists/{correct_list.id}/')
        self.assertEqual(response.context['list'], correct_list)


    # def test_displays_all_items(self):
    def test_displays_only_items_for_that_list(self):

        current_list = List.objects.create()
        Item.objects.create(text='itemey 1', list=current_list)
        Item.objects.create(text='itemey 2', list=current_list)

        other_list = List.objects.create()
        Item.objects.create(text='other list item 1', list=other_list)
        Item.objects.create(text='other list item 2', list=other_list)

        response = self.client.get(f'/lists/{current_list.id}/')

        self.assertContains(response, 'itemey 1')
        self.assertContains(response, 'itemey 2')
        self.assertNotContains(response, 'other list item 1')
        self.assertNotContains(response, 'other list item 2')

    def test_can_save_a_POST_request_to_an_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'A new item for an existing list'}
        )
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for an existing list')
        self.assertEqual(new_item.list, correct_list)

    def test_redirect_to_list_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'A new item for an existing list'},
        )

        self.assertRedirects(response, f'/lists/{correct_list.id}/')

    
    def test_duplicate_item_validation_errors_end_up_on_list_page(self):
        list1 = List.objects.create()
        item1 = Item.objects.create(text='textey', list=list1)
        response = self.client.post(
            f'/lists/{list1.id}/',
            data={'text' : 'textey'}
        )

        expected_error = escape(DUPLICATE_ITEM_ERROR)
        self.assertContains(response, expected_error)
        self.assertTemplateUsed(response, 'list.html')
        self.assertEqual(Item.objects.count(), 1)


    # def test_validation_errors_end_up_on_lists_page(self):
    #     list_ = List.objects.create()
    #     response = self.client.post(
    #         f'/lists/{list_.id}/',
    #         data={'text' : ''}
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'list.html')
    #     expected_error = escape("You can't have an empty list item")
    #     self.assertContains(response, expected_error)
    def post_invalid_input(self):
        list_ = List.objects.create()
        return self.client.post(
            f'/lists/{list_.id}/',
            data={'text' : ''}
        )

    def test_for_invalid_input_nothing_saved_to_db(self):
        self.post_invalid_input()
        self.assertEqual(Item.objects.count(), 0)

    def test_for_invalid_input_list_template(self):
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.post_invalid_input()
        self.assertIsInstance(response.context['form'], ExistingListItemForm)

    def test_for_invalid_input_shows_error_on_page(self):
        response = self.post_invalid_input()
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))
        
    
    def test_displays_item_form(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertIsInstance(response.context['form'], ExistingListItemForm)
        self.assertContains(response, 'name="text')

class NewListViewIntegratedTest(TestCase):
    def test_can_save_a_POST_request(self):
        response = self.client.post('/lists/new', data={'text' : 'A new list item'})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test_redirects_after_POST(self):
        response = self.client.post('/lists/new', data={'text' : 'A new list item'})
        # self.assertEqual(response.status_code, 302)
        # self.assertEqual(response['location'], '/lists/the-only-list-in-the-world/')
        new_list = List.objects.first()
        self.assertRedirects(response, f'/lists/{new_list.id}/')

    def test_for_invalid_input_renders_home_template(self):
        response = self.client.post('/lists/new', data={'text' : ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_validation_errors_are_shown_on_home_page(self):
        response = self.client.post('/lists/new', data={'text' : ''})
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_for_invalid_input_passesform_to_template(self):
        reseponse = self.client.post('/lists/new', data={'text' : ''})
        self.assertIsInstance(reseponse.context['form'], ItemForm)

    def test_invalid_list_items_arent_saved(self):
        self.client.post('/lists/new', data={'text' : ''})
        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)


    def test_list_owner_is_saved_if_user_authenticated(self):
        user = User.objects.create(email='a@b.com')
        self.client.force_login(user)
        self.client.post('/lists/new', data={'text' : 'new item'})
        list_ = List.objects.first()
        self.assertEqual(list_.owner, user)

@patch('lists.views.NewListForm')
class NewListViewUnitTest(TestCase):
    def setUp(self):
        self.request = HttpRequest()
        self.request.POST['text'] = 'new list item'
        self.request.user = Mock()

    def test_passes_POST_data_to_NewListForm(self, mockNewListForm):
        new_list(self.request)
        mockNewListForm.assert_called_once_with(data=self.request.POST)

    def test_saves_form_with_owner_if_form_valid(self, mockNewListForm):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = True
        new_list(self.request)
        mock_form.save.assert_called_once_with(owner=self.request.user)

    @patch('lists.views.redirect')
    def test_redirects_to_form_returned_object_if_form_valid(self, mock_redirect, mockNewListForm):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = True

        response = new_list(self.request)
        
        self.assertEqual(response, mock_redirect.return_value)
        mock_redirect.assert_called_once_with(
            str(mock_form.save.return_value.get_absolute_url()),
        )

    @patch('lists.views.render')
    def test_renders_home_template_with_form_if_form_invalid(self, mock_render, mockNewListForm):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = False

        response = new_list(self.request)

        self.assertEqual(response, mock_render.return_value)
        mock_render.assert_called_once_with(
            self.request, 'home.html', {'form' : mock_form},
        )
        
    def test_doen_not_save_if_form_is_invalid(self, mockNewListForm):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = False

        new_list(self.request)

        self.assertFalse(mock_form.save.called)



class MyListsTest(TestCase):
    def test_my_lists_url_renders_my_lists_template(self):
        User.objects.create(email='a@b.com')
        response = self.client.get('/lists/users/a@b.com/')
        self.assertTemplateUsed(response, 'my_lists.html')

    def test_passes_correct_owner_to_template(self):
        User.objects.create(email='wrong@owner.com')
        correct_user = User.objects.create(email='a@b.com')

        response = self.client.get('/lists/users/a@b.com/')
        self.assertEqual(response.context['owner'], correct_user)

    def test_return_shared_lists_too(self):
        user1 = User.objects.create(email='a@a.com')
        self.client.post('/lists/new', data={'text' : 'new item'})
        list_ = List.objects.first()
        email = 'b@b.com'
        self.client.post(
            f'/lists/{list_.id}/share',
            data={'sharee' : email},
        )
        response = self.client.get(f'/lists/users/{email}/')
        self.assertIn('shared_lists', response.context.keys())
        self.assertIn(
            'new item',
             [list_.name for list_ in response.context['shared_lists']]
        )

    

class ShareListViewTest(TestCase):

    def test_post_redirects_to_lists_page(self):
        list_ = List.objects.create()
        user1 = User.objects.create(email='a@b.com')
        email = 'b@b.com'
        friend = User.objects.create(email=email)
        response = self.client.post(
            f'/lists/{list_.id}/share',
            data={'sharee' : email},
        )

        self.assertRedirects(response, f'/lists/{list_.id}/')

    def test_post_share_list_with_existing_email(self):
        user1 = User.objects.create(email='a@b.com')
        self.client.post('/lists/new', data={'text' : 'new item'})
        list_ = List.objects.create()

        email = 'b@b.com'
        friend = User.objects.create(email=email)
        response = self.client.post(
            f'/lists/{list_.id}/share',
            data={'sharee' : email},
        )

        self.assertIn(friend, list_.shared_with.all())

    def test_post_share_list_and_register_email(self):
        user1 = User.objects.create(email='a@b.com')
        self.client.post('/lists/new', data={'text' : 'new item'})
        list_ = List.objects.create()

        email = 'b@b.com'
        response = self.client.post(
            f'/lists/{list_.id}/share',
            data={'sharee' : email},
        )
        friend = User.objects.get(email=email)

        self.assertIn(friend, list_.shared_with.all())
