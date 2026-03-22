<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Http\Requests\Admin\PermissionStoreRequest;
use App\Http\Requests\Admin\PermissionUpdateRequest;
use App\Models\Permission;
use App\Traits\HasCrud;
use App\Utils\CrudConfig;

class PermissionController extends Controller
{
    use HasCrud;

    public function __construct()
    {
        $this->init(new CrudConfig(
            resource: 'permissions',
            modelClass: Permission::class,
            storeRequestClass: PermissionStoreRequest::class,
            updateRequestClass: PermissionUpdateRequest::class,
            componentPath: 'Admin/Permissions/Index',
            searchColumns: ['name'],
        ));
    }
}
