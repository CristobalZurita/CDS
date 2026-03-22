<?php

namespace App\Utils;

class CrudConfig
{
    public string $resource;

    public string $modelClass;

    public string $storeRequestClass;

    public string $updateRequestClass;

    public ?string $componentPath;

    public ?array $searchColumns;

    public ?string $exportClass;

    public ?array $withRelations;

    public ?array $addProps;

    public function __construct(
        string $resource,
        string $modelClass,
        string $storeRequestClass,
        string $updateRequestClass,
        ?string $componentPath = '',
        ?array $searchColumns = [],
        ?string $exportClass = '',
        ?array $withRelations = [],
        ?array $addProps = [],
    ) {
        $this->resource = $resource;
        $this->modelClass = $modelClass;
        $this->storeRequestClass = $storeRequestClass;
        $this->updateRequestClass = $updateRequestClass;
        $this->componentPath = $componentPath;
        $this->searchColumns = $searchColumns;
        $this->exportClass = $exportClass;
        $this->withRelations = $withRelations;
        $this->addProps = $addProps;
    }
}
