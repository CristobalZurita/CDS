<?php

use App\Http\Controllers\CategoryController;
use App\Http\Controllers\CommentController;
use App\Http\Controllers\DashboardController;
use App\Http\Controllers\ProfileController;
use App\Http\Controllers\TeamController;
use App\Http\Controllers\TicketController;
use App\Http\Controllers\UserController;
use Illuminate\Foundation\Application;
use Illuminate\Support\Facades\Route;
use Inertia\Inertia;

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
|
| Here is where you can register web routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| contains the "web" middleware group. Now create something great!
|
*/

Route::get('/', function () {

    return redirect()->route('dashboard');

//    return Inertia::render('Welcome', [
//        'canLogin' => Route::has('login'),
//        'canRegister' => Route::has('register'),
//    ]);
});

/**
 * Admin and Manager routes
 */

Route::middleware(['auth', 'role.check:admin,manager'])->group(function () {
    Route::put('tickets/{ticket}/assign-users', [TicketController::class, 'assignUsers'])->name('tickets.assign-users');
    Route::put('tickets/{ticket}/assign-teams', [TicketController::class, 'assignTeams'])->name('tickets.assign-teams');
    Route::put('tickets/{ticket}/update-status', [TicketController::class, 'updateStatus'])->name('tickets.update-status');

    Route::get('categories/dataTable', [CategoryController::class, 'dataTable'])->name('categories.dataTable');
    Route::get('users/dataTable', [UserController::class, 'dataTable'])->name('users.dataTable');
    Route::get('teams/dataTable', [TeamController::class, 'dataTable'])->name('teams.dataTable');

    Route::get('teams/my-team', [TeamController::class, 'myTeam'])->name('teams.my-team');

    Route::resource('teams', TeamController::class);
});

/**
 * Admin routes
 */
Route::middleware(['auth', 'role.check:admin'])->group(function () {
    Route::resource('categories', CategoryController::class);

    Route::resource('users', UserController::class);
});



Route::middleware('auth')->group(function () {

    Route::get('dashboard', [DashboardController::class, 'index'])->name('dashboard');

    Route::get('/profile', [ProfileController::class, 'edit'])->name('profile.edit');
    Route::patch('/profile', [ProfileController::class, 'update'])->name('profile.update');
    Route::delete('/profile', [ProfileController::class, 'destroy'])->name('profile.destroy');

    Route::get('tickets/dataTable', [TicketController::class, 'dataTable'])->name('tickets.dataTable');
    Route::resource('tickets', TicketController::class);

    Route::resource('comments', CommentController::class);
});

require __DIR__.'/auth.php';
