<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\SubCategoryStoreRequest;
use App\Http\Requests\SubCategoryUpdateRequest;
use App\Models\SubCategory;
use App\Traits\HasApiCrud;
use App\Utils\CrudConfig;

class SubCategoryController extends Controller
{
    use HasApiCrud;

    public function __construct()
    {
        $this->init(new CrudConfig(
            resource: 'sub-categories',
            modelClass: SubCategory::class,
            storeRequestClass: SubCategoryStoreRequest::class,
            updateRequestClass: SubCategoryUpdateRequest::class,
            searchColumns: ['name'],
        ));
    }
}
