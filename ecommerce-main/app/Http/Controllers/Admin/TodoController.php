<?php

namespace App\Http\Controllers\Admin;

use App\Exports\TodoExport;
use App\Http\Controllers\Controller;
use App\Http\Requests\Admin\TodoStoreRequest;
use App\Http\Requests\Admin\TodoUpdateRequest;
use App\Models\Todo;
use App\Traits\HasCrud;
use App\Utils\CrudConfig;

class TodoController extends Controller
{
    use HasCrud;

    public function __construct()
    {
        $this->init(new CrudConfig(
            resource: 'todos',
            modelClass: Todo::class,
            storeRequestClass: TodoStoreRequest::class,
            updateRequestClass: TodoUpdateRequest::class,
            componentPath: 'Admin/Todos/Index',
            searchColumns: ['title'],
            exportClass: TodoExport::class,
            withRelations: [],
        ));
    }
}
