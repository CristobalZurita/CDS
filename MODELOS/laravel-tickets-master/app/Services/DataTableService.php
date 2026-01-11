<?php

namespace App\Services;

use Illuminate\Contracts\Pagination\LengthAwarePaginator;;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Http\Request;

class DataTableService {

    /**
     * @param Request $request
     * @param Builder $queryBuilder
     * @param array $modelColumns
     * @param null $wihRelations
     * @return LengthAwarePaginator
     */
    public static function data(Request $request, Builder $queryBuilder, array $modelColumns, $wihRelations = null): LengthAwarePaginator {
        $perPage = $request->query('perPage', 10);
        $page = $request->query('page', 1);
        $sortBy = $request->query('sortColumn', 'id');
        $sortDirection = $request->query('sort', 'desc');
        $search = $request->query('search');

        $columns = $request->query('columns', ['*']);

        $queryBuilder->where(function (Builder $query) use ($modelColumns, $search) {
            foreach ($modelColumns as $modelColumn) {
                $query->orWhere($modelColumn, 'like', '%' . $search . '%');
            }
        });

        if ($wihRelations) {
            $queryBuilder->with($wihRelations);
        }

        $queryBuilder->orderBy($sortBy, $sortDirection);

        return $queryBuilder->paginate($perPage, $columns, 'page', $page);
    }
}
