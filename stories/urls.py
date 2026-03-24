from django.urls import path
from . import views
from . import views_admin

urlpatterns = [
    # Người đọc
    path('', views.home, name='home'),
    path('truyen/<int:story_id>/', views.story_detail, name='story_detail'),
    path('truyen/<int:story_id>/doc/<int:chapter_number>/', views.read_chapter, name='read_chapter'),
    path('huong-dan-lay-mat-khau/', views.get_password_guide, name='get_password_guide'),
    # Admin - không dùng session
    path('admin-panel/', views_admin.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/add-story/', views_admin.admin_add_story, name='admin_add_story'),
    path('admin-panel/story/<int:story_id>/delete/', views_admin.admin_delete_story, name='admin_delete_story'),
    path('admin-panel/story/<int:story_id>/chapters/', views_admin.admin_manage_chapters, name='admin_manage_chapters'),
    path('admin-panel/story/<int:story_id>/add-chapter/', views_admin.admin_add_chapter, name='admin_add_chapter'),
    path('admin-panel/story/<int:story_id>/chapter/<int:chapter_id>/edit/', views_admin.admin_edit_chapter, name='admin_edit_chapter'),
    path('admin-panel/story/<int:story_id>/chapter/<int:chapter_id>/delete/', views_admin.admin_delete_chapter, name='admin_delete_chapter'),
    path('admin-panel/story/<int:story_id>/bulk-delete-chapters/', views_admin.admin_bulk_delete_chapters, name='admin_bulk_delete_chapters'),
]