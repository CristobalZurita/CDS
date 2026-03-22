<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\TodoStoreRequest;
use App\Http\Requests\TodoUpdateRequest;
use App\Models\Todo;
use App\Traits\HasApiCrud;
use App\Utils\CrudConfig;

class TodoController extends Controller
{
    use HasApiCrud;

    public function __construct()
    {
        $this->init(new CrudConfig(
            resource: 'todos',
            modelClass: Todo::class,
            storeRequestClass: TodoStoreRequest::class,
            updateRequestClass: TodoUpdateRequest::class,
            searchColumns: ['title'],
        ));
    }
}
