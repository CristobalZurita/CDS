<?php

namespace Tests\Feature\Controllers;

use App\Models\Category;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Storage;
use Inertia\Testing\AssertableInertia as Assert;
use Tests\TestCase;

class CategoryControllerTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        Storage::fake('public');
        $this->actingAs(User::factory()->create());
    }

    public function test_index_displays_categories()
    {
        // Arrange

        // Act
        $response = $this->get(route('categories.index'));

        // Assert
        $response->assertStatus(200);
        $response->assertInertia(
            fn (Assert $page) => $page
                ->component('Categories/Index')
            // ->has('categories.data', 15);
        );
    }

    public function test_store_creates_new_category()
    {
        // Arrange
        $categoryData = [
            'name' => 'Test Category',
            'is_active' => false,
        ];

        // Act
        $response = $this->post(route('categories.store'), $categoryData);

        // Assert
        $response->assertRedirect(route('categories.index'));
        $response->assertSessionHas('success');
        $this->assertDatabaseHas('categories', $categoryData);
    }

    public function test_store_creates_category_with_photo()
    {
        // Arrange
        $photo = UploadedFile::fake()->image('category.jpg');
        $categoryData = [
            'name' => 'Test Category',
            'photo' => $photo,
        ];

        // Act
        $response = $this->post(route('categories.store'), $categoryData);

        // Assert
        $response->assertRedirect(route('categories.index'));
        $response->assertSessionHas('success');

        $category = Category::first();
        $this->assertNotNull($category->photo);
        Storage::disk('public')->assertExists($category->photo);
    }

    public function test_update_category()
    {
        // Arrange
        $category = Category::factory()->create();
        $updateData = [
            'name' => 'Updated Name',
            'is_active' => false,
        ];

        // Act
        $response = $this->put(route('categories.update', $category), $updateData);

        // Assert
        $response->assertRedirect(route('categories.index'));
        $response->assertSessionHas('success');
        $this->assertDatabaseHas('categories', $updateData);
    }

    public function test_update_category_with_new_photo()
    {
        // Arrange
        $category = Category::factory()->create([
            'photo' => 'categories/old-photo.jpg',
        ]);
        Storage::put($category->photo, 'fake-old-image');

        $newPhoto = UploadedFile::fake()->image('new-category.jpg');
        $updateData = [
            'name' => 'Updated Name',
            'photo' => $newPhoto,
        ];

        // Act
        $response = $this->put(route('categories.update', $category), $updateData);

        // Assert
        $response->assertRedirect(route('categories.index'));
        $response->assertSessionHas('success');

        $category->refresh();
        Storage::assertMissing('categories/old-photo.jpg');
        Storage::assertExists($category->photo);
    }

    public function test_destroy_category()
    {
        // Arrange
        $category = Category::factory()->create([
            'photo' => 'categories/test-photo.jpg',
        ]);
        Storage::put($category->photo, 'fake-image');

        // Act
        $response = $this->delete(route('categories.destroy', $category));

        // Assert
        $response->assertRedirect(route('categories.index'));
        $response->assertSessionHas('success');
        $this->assertDatabaseMissing('categories', [['id' => $category->id]]);
        Storage::assertMissing($category->photo);
    }

    public function test_bulk_destroy_categories()
    {
        // Arrange
        $categories = Category::factory(3)->create()->each(function ($category) {
            $category->photo = 'categories/test-photo-'.$category->id.'.jpg';
            $category->save();
            Storage::put($category->photo, 'fake-image');
        });

        $categoryIds = $categories->pluck('id')->toArray();

        // Act
        $response = $this->post(route('categories.bulk-destroy'), [
            'categoryIds' => $categoryIds,
        ]);

        // Assert
        $response->assertRedirect(route('categories.index'));
        $response->assertSessionHas('success');

        foreach ($categories as $category) {
            $this->assertDatabaseMissing('categories', [['id' => $category->id]]);
            Storage::assertMissing($category->photo);
        }
    }

    public function test_bulk_destroy_validates_category_ids()
    {
        // Act
        $response = $this->delete(route('categories.bulk-destroy'), [
            'categoryIds' => 'not-an-array',
        ]);

        // Assert
        $response->assertStatus(302);
        $response->assertSessionHasErrors(['categoryIds']);
    }
}
