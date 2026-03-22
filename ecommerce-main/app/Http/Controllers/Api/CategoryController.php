<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\CategoryStoreRequest;
use App\Http\Requests\CategoryUpdateRequest;
use App\Models\Category;
use App\Traits\HasApiCrud;
use App\Utils\CrudConfig;

class CategoryController extends Controller
{
    use HasApiCrud;

    public function __construct()
    {
        $this->init(new CrudConfig(
            resource: 'categories',
            modelClass: Category::class,
            storeRequestClass: CategoryStoreRequest::class,
            updateRequestClass: CategoryUpdateRequest::class,
            searchColumns: ['name'],
        ));
    }
}
