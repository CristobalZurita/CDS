<?php

namespace App\Models;

// use Illuminate\Contracts\Auth\MustVerifyEmail;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\SoftDeletes;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens;

class User extends Authenticatable {
    use HasApiTokens, HasFactory, Notifiable, SoftDeletes;

    /**
     * The attributes that are mass assignable.
     *
     * @var array<int, string>
     */
    protected $fillable = [
        'name',
        'email',
        'password',
        'role'
    ];

    protected $appends = [
        'avatar'
    ];

    public function getAvatarAttribute(): string {
        $encodedName = urlencode($this->name);
        return "https://ui-avatars.com/api/?name={$encodedName}&background=random";
    }

    const ROLES = [
        'admin', 'manager', 'team_lead', 'team_member', 'customer'
    ];

    /**
     * The attributes that should be hidden for serialization.
     *
     * @var array<int, string>
     */
    protected $hidden = [
        'password',
        'remember_token',
    ];

    /**
     * The attributes that should be cast.
     *
     * @var array<string, string>
     */
    protected $casts = [
        'email_verified_at' => 'datetime',
        'password' => 'hashed',
    ];

    public function isAdmin(): bool {
        return $this->role == 'admin';
    }

    public function isManager(): bool {
        return $this->role == 'manager';
    }

    public function isCustomer(): bool {
        return $this->role == 'customer';
    }

    public function isTeamMember(): bool {
        return $this->role == 'team_member';
    }

    public function isTeamLead(): bool {
        return $this->role == 'team_lead';
    }

    public function tickets(): HasMany {
        return $this->hasMany(Ticket::class);
    }

    public function teams(): BelongsToMany {
        return $this->belongsToMany(Team::class);
    }

    public function assignedTickets(): BelongsToMany {
        return $this->belongsToMany(Ticket::class, 'ticket_user');
    }

    public function comments(): HasMany {
        return $this->hasMany(Comment::class);
    }
}
