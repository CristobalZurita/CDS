<?php

namespace App\Policies;

use App\Models\Ticket;
use App\Models\User;
use Illuminate\Auth\Access\HandlesAuthorization;
use Illuminate\Database\Eloquent\Builder;

class TicketPolicy {
    use HandlesAuthorization;

    /**
     * @param User $user
     * @return bool
     */
    public function viewAny(User $user): bool {
        return true;
    }

    /**
     * @param User $user
     * @param Ticket $ticket
     * @return bool
     */
    public function view(User $user, Ticket $ticket): bool {
        if ($user->isAdmin()) {
            return true;
        }

        if ($user->isCustomer()) {
            return $ticket->user_id == $user->id;
        }

        if ($user->isManager()) {
            return $ticket->assignedTeams()->where('manager_id', $user->id)->exists();
        }

        if ($user->isTeamLead() || $user->isTeamMember()) {
            return $ticket->assignedTeams()->whereHas('users', function (Builder $query) use ($user) {
                $query->where('users.id', $user->id);
            })->exists();
        }

        return false;
    }

    /**
     * @param User $user
     * @return bool
     */
    public function create(User $user): bool {
        return true; // everyone can create ticket
    }

    public function update(User $user): bool {
        return $user->isAdmin();
    }

    /**
     * @param User $user
     * @param Ticket $ticket
     * @return bool
     */
    public function updateStatus(User $user, Ticket $ticket): bool {
        if ($user->isAdmin()) {
            return true;
        }

        if ($user->isManager()) {
            return $ticket->assignedTeams()->where('manager_id', $user->id)->exists();
        }

        if ($user->isTeamLead() || $user->isTeamMember()) {
            return $ticket->assignedUsers()->where('users.id', $user->id)->exists();
        }

        return false;
    }

    /**
     * @param User $user
     * @param Ticket $ticket
     * @return bool
     */
    public function assignUsers(User $user, Ticket $ticket): bool {
        if ($user->isAdmin()) {
            return true;
        }

        if ($user->isManager()) {
            return $ticket->assignedTeams()->where('manager_id', $user->id)->exists();
        }

        return false;
    }

    public function assignTeams(User $user, Ticket $ticket): bool {
        return $user->isAdmin();
    }

    /**
     * @param User $user
     * @param Ticket $ticket
     * @return bool
     */
    public function addComment(User $user, Ticket $ticket): bool {

        if ($user->isAdmin()) {
            return true;
        }

        if ($user->isManager()) {
            return $ticket->assignedTeams()->where('manager_id', $user->id)->exists();
        }

        if ($user->isTeamLead() || $user->isTeamMember()) {
            return $ticket->assignedUsers()->where('users.id', $user->id)->exists();
        }

        if ($user->isCustomer()) {
            return $ticket->user_id === $user->id;
        }

        return false;
    }
}
