<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
// use App\Exports\PaymentMethodExport;
use App\Http\Requests\Admin\PaymentMethodStoreRequest;
use App\Http\Requests\Admin\PaymentMethodUpdateRequest;
use App\Models\PaymentMethod;
use App\Traits\HasCrud;
use App\Utils\CrudConfig;

class PaymentMethodController extends Controller
{
    use HasCrud;

    public function __construct()
    {
        $this->init(new CrudConfig(
            resource: 'payment-methods',
            modelClass: PaymentMethod::class,
            storeRequestClass: PaymentMethodStoreRequest::class,
            updateRequestClass: PaymentMethodUpdateRequest::class,
            componentPath: 'Admin/PaymentMethods/Index',
            searchColumns: ['name'],
            // exportClass: PaymentMethodExport::class,
            withRelations: [],
        ));
    }
}
