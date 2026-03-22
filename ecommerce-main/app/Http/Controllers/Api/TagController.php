<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\TagStoreRequest;
use App\Http\Requests\TagUpdateRequest;
use App\Models\Tag;
use App\Traits\HasApiCrud;
use App\Utils\CrudConfig;

class TagController extends Controller
{
    use HasApiCrud;

    public function __construct()
    {
        $this->init(new CrudConfig(
            resource: 'tags',
            modelClass: Tag::class,
            storeRequestClass: TagStoreRequest::class,
            updateRequestClass: TagUpdateRequest::class,
            searchColumns: ['name'],
        ));
    }
}
