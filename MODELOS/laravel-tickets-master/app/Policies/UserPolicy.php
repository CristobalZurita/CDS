<?php

namespace App\Policies;

use App\Models\User;
use Illuminate\Auth\Access\HandlesAuthorization;

class UserPolicy {
    use HandlesAuthorization;

    public function before(User $user) {
        if ($user->isAdmin()) {
            return true;
        }
    }

    public function viewAny(User $user): bool {
        return $user->isManager() || $user->isTeamLead() || $user->isTeamMember();
    }

    public function view(User $user, User $model): bool {
        if ($user->isManager()) {
            return $user->teams()->whereHas('users', function($query) use ($model) {
                $query->where('users.id', $model->id);
            })->exists();
        }

        if ($user->isTeamLead() || $user->isTeamMember()) {
            return $user->teams()->whereHas('users', function ($query) use ($model) {
                $query->where('users.id', $model->id);
            })->exists();
        }

        return false;
    }

    public function create(User $user): bool {
        return $user->isManager();
    }

    public function update(User $user, User $model): bool {
        return false;
    }

    public function delete(User $user, User $model): bool {
        return false;
    }
}
