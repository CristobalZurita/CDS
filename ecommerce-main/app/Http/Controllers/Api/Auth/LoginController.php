<?php

namespace App\Http\Controllers\Api\Auth;

use App\Http\Controllers\Controller;
use App\Http\Requests\Api\Auth\UserLoginRequest;
use App\Models\User;
use Illuminate\Http\Response;
use Illuminate\Support\Facades\Auth;

class LoginController extends Controller
{
    public function login(UserLoginRequest $request)
    {
        $credentials = $request->validated();
        $user = User::where('email', $credentials['email'])->first();
        $isVerified = $user->hasVerifiedEmail();
        if ($isVerified && Auth::attempt($credentials)) {
            $token = auth()->user()->createToken('login-token')->plainTextToken;

            return response()->json([
                'data' => auth()->user(),
                'token' => $token,
            ]);
        }

        if (! $isVerified) {
            return response()->json([
                'data' => null,
                'message' => 'Your account is not verified yet. Please verify in order to login.',
                'status_code' => Response::HTTP_FORBIDDEN,
            ], Response::HTTP_FORBIDDEN);
        }

        return response()->json([
            'data' => null,
            'message' => 'Login failed, please try again with correct credentials.',
            'status_code' => Response::HTTP_UNAUTHORIZED,
        ], Response::HTTP_UNAUTHORIZED);
    }
}
