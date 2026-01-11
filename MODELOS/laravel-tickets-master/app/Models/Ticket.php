<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\SoftDeletes;

class Ticket extends Model {
    use SoftDeletes;
    use HasFactory;

    protected $fillable = [
        'title',
        'ticket_number',
        'description',
        'user_id',
        'category_id',
        'status',
    ];

    const TICKET_STATUSES = ['backlog', 'open', 'resolved', 'closed'];

    protected static function boot(): void {
        parent::boot();

        self::created(function (Ticket $ticket) {
            $randomNumber = rand(10000000, 99999999);
            $ticket->ticket_number = substr($ticket->id . $randomNumber, -8);

            $categoryId = $ticket->category_id;
            $team = Team::whereHas('categories', function (Builder $query) use ($categoryId) {
                $query->where('categories.id', $categoryId);
            })->inRandomOrder()->first();

            if ($team) {
                $ticket->assignedTeams()->attach($team->id);
            }

            $ticket->save();
        });
    }


    /**
     * @return BelongsTo
     */
    public function user(): BelongsTo {
        return $this->belongsTo(User::class);
    }

    /**
     * @return BelongsTo
     */
    public function category(): BelongsTo {
        return $this->belongsTo(Category::class);
    }


    public function assignedUsers(): BelongsToMany {
        return $this->belongsToMany(User::class, 'ticket_user');
    }

    public function comments(): HasMany {
        return $this->hasMany(Comment::class);
    }

    public function assignedTeams(): BelongsToMany {
        return $this->belongsToMany(Team::class, 'ticket_team');
    }
}
