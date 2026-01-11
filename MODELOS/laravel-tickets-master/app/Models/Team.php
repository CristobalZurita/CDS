<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\SoftDeletes;

class Team extends Model {
    use SoftDeletes;
    use HasFactory;

    protected $fillable = [
        'name',
        'description',
        'manager_id',
    ];

    public function manager(): BelongsTo {
        return $this->belongsTo(User::class, 'manager_id', 'id');
    }

    public function tickets(): BelongsToMany {
        return $this->belongsToMany(Ticket::class, 'team_id', 'id');
    }

    public function users(): BelongsToMany {
        return $this->belongsToMany(User::class);
    }

    public function categories(): BelongsToMany {
        return $this->belongsToMany(Category::class, 'category_team');
    }

}
