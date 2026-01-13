<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\SoftDeletes;

class Category extends Model {
    use SoftDeletes;
    use HasFactory;

    protected $fillable = [
        'name',
        'description',
        'category_id'
    ];

    /**
     * @return BelongsTo
     */
    public function category(): BelongsTo {
        return $this->belongsTo(Category::class);
    }

    public function tickets(): HasMany {
        return $this->hasMany(Ticket::class);
    }

    public function teams(): BelongsToMany {
        return $this->belongsToMany(Team::class, 'category_team');
    }
}
