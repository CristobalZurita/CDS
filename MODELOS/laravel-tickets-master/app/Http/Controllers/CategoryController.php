<?php

namespace App\Http\Controllers;

use App\Http\Requests\CategoryRequest;
use App\Http\Resources\CategoryCollection;
use App\Models\Category;
use App\Services\DataTableService;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;

class CategoryController extends Controller {

    /**
     * @return Response
     */
    public function index() {
        $this->authorize('viewAny', Category::class);
        return Inertia::render('Categories/Index');
    }

    /**
     * @param Request $request
     * @return CategoryCollection
     */
    public function dataTable(Request $request) {

        $columns = [
            'name',
            'description',
            'category_id'
        ];

        $query = Category::query()
            ->when($request->query('team'), function (Builder $query) use ($request) {
                $teamId = $request->query('team');
                $query->whereHas('teams', function (Builder $query) use ($teamId) {
                    $query->where('teams.id', $teamId);
                });
            });

        $categories = DataTableService::data($request, $query, $columns);

        return new CategoryCollection($categories);
    }

    public function create() {
        $categories = Category::all()->toArray();
        return Inertia::render('Categories/CreateEdit', ['categories' => $categories]);
    }

    /**
     * @param CategoryRequest $request
     * @return RedirectResponse
     */
    public function store(CategoryRequest $request) {
        $this->authorize('create', Category::class);
        $category = Category::create($request->validated());
        return redirect()->route('categories.edit', $category->id)
            ->with('success', 'Category created.');
    }

    /**
     * @param Category $category
     * @return Response
     */
    public function edit(Category $category) {
        $categories = Category::all()->toArray();
        return Inertia::render('Categories/CreateEdit', ['categories' => $categories, 'category' => $category]);
    }

    public function show(Category $category) {
        return $category;
    }

    /**
     * @param CategoryRequest $request
     * @param Category $category
     * @return RedirectResponse
     */
    public function update(CategoryRequest $request, Category $category) {
        $this->authorize('update', $category);

        $category->update($request->validated());

        return redirect()->route('categories.index')
            ->with('success', 'Category updated.');
    }

    /**
     * @param Category $category
     * @return true[]
     */
    public function destroy(Category $category) {
        $this->authorize('delete', $category);
        $category->delete();

        return [
            'success' => true,
        ];
    }
}
