<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void {
        Schema::create('category_team', function (Blueprint $table) {

            $table->foreignId('category_id')->constrained('categories');
            $table->foreignId('team_id')->constrained('teams');
            $table->primary(['category_id', 'team_id']);

            $table->timestamps();
        });
    }

    public function down(): void {
        Schema::dropIfExists('category_team');
    }
};
