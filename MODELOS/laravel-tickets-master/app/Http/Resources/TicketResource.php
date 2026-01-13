<?php

namespace App\Http\Resources;

use Carbon\Carbon;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class TicketResource extends JsonResource {

    public static $wrap = null;

    public function toArray(Request $request): array {
        return [
            'id' => $this->id,
            'title' => $this->title,
            'ticket_number' => $this->ticket_number,
            'description' => $this->description,
            'user_id' => $this->user_id,
            'category_id' => $this->category_id,
            'parent' => $this->category?->name,
            'status' => $this->status,

            'user' => new UserResource($this->user),
            'assignedUsers' => UserResource::collection($this->assignedUsers),
            'category' => new CategoryResource($this->category),
            'comments' => CommentResource::collection($this->comments),
            'assignedTeams' => UserResource::collection($this->assignedTeams),

            'created_at' => Carbon::make($this->created_at)->format('Y-m-d H:i:s'),
            'updated_at' => Carbon::make($this->updated_at)->format('Y-m-d H:i:s'),
        ];
    }
}
