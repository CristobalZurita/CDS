<?php

namespace App\Http\Controllers\Admin;

use App\Exports\TagExport;
use App\Http\Controllers\Controller;
use App\Http\Requests\Admin\TagStoreRequest;
use App\Http\Requests\Admin\TagUpdateRequest;
use App\Models\Tag;
use App\Traits\HasCrud;
use App\Utils\CrudConfig;

class TagController extends Controller
{
    use HasCrud;

    public function __construct()
    {
        $this->init(new CrudConfig(
            resource: 'tags',
            modelClass: Tag::class,
            storeRequestClass: TagStoreRequest::class,
            updateRequestClass: TagUpdateRequest::class,
            componentPath: 'Admin/Tags/Index',
            searchColumns: ['name'],
            exportClass: TagExport::class,
            withRelations: [],

        ));
    }
}
