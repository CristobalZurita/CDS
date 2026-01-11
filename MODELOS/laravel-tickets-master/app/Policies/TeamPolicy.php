<?php

namespace App\Policies;

use App\Models\Team;
use App\Models\User;
use Illuminate\Auth\Access\HandlesAuthorization;

class TeamPolicy {
    use HandlesAuthorization;

    public function before(User $user) {
        if ($user->isAdmin()) {
            return true;
        }
    }

    public function viewAny(User $user): bool {
        return $user->isAdmin();
    }

    /**
     * @param User $user
     * @param Team $team
     * @return bool
     */
    public function view(User $user, Team $team): bool {
        if ($user->isManager()) {
            return $team->manager_id === $user->id;
        }

        if ($user->isTeamLead() || $user->isTeamMember()) {
            return $team->users()->whereHas('users.id', $user->id)->exists();
        }

        return false;
    }

    /**
     * @param User $user
     * @return bool
     */
    public function myTeam(User $user): bool {
        return $user->isManager();
    }

    /**
     * @param User $user
     * @return bool
     */
    public function create(User $user): bool {
        return false;
    }

    /**
     * @param User $user
     * @param Team $team
     * @return bool
     */
    public function update(User $user, Team $team): bool {
        return false;
    }

    /**
     * @param User $user
     * @param Team $team
     * @return bool
     */
    public function delete(User $user, Team $team): bool {
        return false;
    }
}
