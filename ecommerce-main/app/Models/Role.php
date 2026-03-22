<?php

namespace App\Models;

use Spatie\Permission\Models\Role as SpatieBaseRole;

class Role extends SpatieBaseRole
{
    protected function casts(): array
    {
        return [
            'created_at' => 'datetime:Y-m-d H:i:a',
        ];
    }
}
