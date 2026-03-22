<?php

declare(strict_types=1);

namespace App\Http\Response;

use Illuminate\Http\Response;

class ApiResponse
{
    public static function ok($data, $status_code = Response::HTTP_OK)
    {
        return response()->json($data);
    }

    public static function success($data, $message = 'Successful!', $status_code = Response::HTTP_OK)
    {
        return response()->json([
            'data' => $data,
            'message' => $message,
        ], $status_code);
    }

    public static function created($data, $message = 'Successfully created!', $status_code = Response::HTTP_CREATED)
    {
        return response()->json([
            'data' => $data,
            'message' => $message,
            'status_code' => $status_code,
        ], $status_code);
    }

    public static function updated($data, $message = 'Successfully updated!', $status_code = Response::HTTP_ACCEPTED)
    {
        return response()->json([
            'data' => $data,
            'message' => $message,
        ], $status_code);
    }

    public static function deleted($data, $message = 'Successfully deleted!', $status_code = Response::HTTP_NO_CONTENT)
    {
        return response()->json([
            'data' => $data,
            'message' => $message,
        ], $status_code);
    }

    public static function error($data = null, $message = 'Something went wrong!', $status_code = Response::HTTP_INTERNAL_SERVER_ERROR)
    {
        return response()->json([
            'data' => $data,
            'message' => $message,
            'status_code' => $status_code,
        ]);
    }
}
