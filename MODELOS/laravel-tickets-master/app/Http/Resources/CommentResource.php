<?php

namespace App\Http\Resources;

use Carbon\Carbon;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class CommentResource extends JsonResource {

    public static $wrap = null;

    public function toArray(Request $request): array {
        return [
            'message' => $this->message,
            'user_id' => $this->user_id,
            'user' => $this->user,
            'ticket_id' => $this->ticket_id,
            'ticket' => $this->ticket,
            'created_at' => Carbon::make($this->created_at)->format('Y-m-d H:i:s'),
        ];
    }
}
