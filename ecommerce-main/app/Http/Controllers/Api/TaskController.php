<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\TaskStoreRequest;
use App\Http\Requests\TaskUpdateRequest;
use App\Models\Task;
use App\Traits\HasApiCrud;
use App\Utils\CrudConfig;

class TaskController extends Controller
{
    use HasApiCrud;

    public function __construct()
    {
        $this->init(new CrudConfig(
            resource: 'task',
            modelClass: Task::class,
            storeRequestClass: TaskStoreRequest::class,
            updateRequestClass: TaskUpdateRequest::class,
            searchColumns: ['title'],
        ));
    }
}
