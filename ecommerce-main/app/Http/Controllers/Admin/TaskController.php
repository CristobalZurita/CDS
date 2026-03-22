<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
// use App\Exports\TaskExport;
use App\Http\Requests\Admin\TaskStoreRequest;
use App\Http\Requests\Admin\TaskUpdateRequest;
use App\Models\Task;
use App\Traits\HasCrud;
use App\Utils\CrudConfig;

class TaskController extends Controller
{
    use HasCrud;

    public function __construct()
    {
        $this->init(new CrudConfig(
            resource: 'tasks',
            modelClass: Task::class,
            storeRequestClass: TaskStoreRequest::class,
            updateRequestClass: TaskUpdateRequest::class,
            componentPath: 'Admin/Tasks/Index',
            searchColumns: [],
            // exportClass: TaskExport::class,
            withRelations: [],
        ));
    }
}
