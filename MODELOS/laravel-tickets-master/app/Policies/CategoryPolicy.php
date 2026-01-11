<?php

namespace App\Policies;

use App\Models\Category;
use App\Models\User;
use Illuminate\Auth\Access\HandlesAuthorization;

class CategoryPolicy {
    use HandlesAuthorization;

    public function before(User $user) {
        if ($user->isAdmin()) {
            return true;
        }
    }

    public function viewAny(User $user): bool {
        return false;
    }

    public function view(User $user, Category $category): bool {
        return false;
    }

    public function create(User $user): bool {
        return false;
    }

    public function update(User $user, Category $category): bool {
        return false;
    }

    public function delete(User $user, Category $category): bool {
        return false;
    }
}
