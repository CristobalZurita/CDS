<?php

namespace App\Utils;

use Illuminate\Support\Facades\Route;

class CrudRouter
{
    public static function setFor($resource, $controller, $middleware = []): void
    {
        Route::middleware($middleware)->group(function () use ($resource, $controller) {
            Route::resource($resource, $controller);
            Route::post($resource.'/action/bulk-destroy', [$controller, 'bulkDestroy'])->name($resource.'.bulk-destroy');
            Route::post($resource.'/action/bulk-restore', [$controller, 'bulkRestore'])->name($resource.'.bulk-restore');
            Route::post($resource.'/action/bulk-force-delete', [$controller, 'bulkForceDelete'])->name($resource.'.bulk-force-delete');
            Route::get($resource.'/action/export-excel', [$controller, 'export'])->name($resource.'.export');
        });
    }

    public static function setApiFor($resource, $controller, $middleware = []): void
    {
        Route::middleware($middleware)->group(function () use ($resource, $controller) {
            Route::apiResource($resource, $controller);
            Route::post($resource.'/action/bulk-destroy', [$controller, 'bulkDestroy'])->name($resource.'.bulk-destroy');
            Route::post($resource.'/action/bulk-restore', [$controller, 'bulkRestore'])->name($resource.'.bulk-restore');
            Route::post($resource.'/action/bulk-force-delete', [$controller, 'bulkForceDelete'])->name($resource.'.bulk-force-delete');
            Route::get($resource.'/action/export-excel', [$controller, 'export'])->name($resource.'.export');
        });
    }
}
