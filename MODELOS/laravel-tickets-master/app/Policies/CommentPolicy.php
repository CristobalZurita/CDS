<?php

namespace App\Policies;

use App\Models\User;
use Illuminate\Auth\Access\HandlesAuthorization;

class CommentPolicy {
    use HandlesAuthorization;

    public function action(User $user): bool {

    }
}
