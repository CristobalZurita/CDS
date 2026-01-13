<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void {
        Schema::create('ticket_team', function (Blueprint $table) {

            $table->foreignId('ticket_id')
                ->constrained()
                ->onUpdate('cascade')
                ->onDelete('cascade');
            $table->foreignId('team_id')
                ->constrained()
                ->onUpdate('cascade')
                ->onDelete('cascade');
            $table->primary(['ticket_id', 'team_id']);

            $table->timestamps();
        });
    }

    public function down(): void {
        Schema::dropIfExists('ticket_team');
    }
};
