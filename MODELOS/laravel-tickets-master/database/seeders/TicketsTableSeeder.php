<?php

namespace Database\Seeders;

use App\Models\Category;
use App\Models\Ticket;
use App\Models\User;
use Illuminate\Database\Seeder;

class TicketsTableSeeder extends Seeder {
    public function run(): void {
        $tickets = [
            ['title' => 'Computer not booting', 'description' => 'The computer fails to boot up properly, showing no signs of power despite being plugged in. This issue might be related to power supply or motherboard. Ensuring proper diagnosis is critical to resolving the issue and preventing further damage.', 'user_id' => User::where('email', 'customer1@example.com')->first()->id, 'category_id' => Category::where('name', 'Computer Hardware Issues')->first()->id, 'status' => 'open'],
            ['title' => 'Software installation failure', 'description' => 'Unable to install necessary software due to compatibility issues or missing dependencies. The installer fails to proceed beyond initial steps. Investigating the root cause and addressing any underlying issues is essential for successful installation.', 'user_id' => User::where('email', 'customer1@example.com')->first()->id, 'category_id' => Category::where('name', 'Computer Software Issues')->first()->id, 'status' => 'backlog'],
            ['title' => 'Printer not connecting', 'description' => 'Printer fails to connect to the computer despite being properly plugged in and powered on. The device is not recognized by the operating system, potentially due to driver issues or connectivity problems. Resolving these issues will ensure smooth printing operations.', 'user_id' => User::where('email', 'customer2@example.com')->first()->id, 'category_id' => Category::where('name', 'Printer Connectivity Issues')->first()->id, 'status' => 'open'],
            ['title' => 'Frequent paper jams', 'description' => 'Printer frequently jams when printing documents. The paper gets stuck inside the printer and needs to be manually removed. This issue disrupts printing tasks and requires thorough investigation to identify and rectify the cause of the jams.', 'user_id' => User::where('email', 'customer2@example.com')->first()->id, 'category_id' => Category::where('name', 'Printer Paper Jams')->first()->id, 'status' => 'open'],
            ['title' => 'Router setup problem', 'description' => 'Unable to configure the router for internet access. The setup wizard fails to detect the internet connection and provide proper settings. Ensuring proper configuration is necessary for establishing a stable and reliable network connection.', 'user_id' => User::where('email', 'customer1@example.com')->first()->id, 'category_id' => Category::where('name', 'Router Configuration Issues')->first()->id, 'status' => 'backlog'],
            ['title' => 'Unstable router connection', 'description' => 'Router connection drops frequently, resulting in intermittent loss of internet access. This issue affects multiple devices connected to the network. Addressing the root cause will ensure consistent and reliable connectivity.', 'user_id' => User::where('email', 'customer2@example.com')->first()->id, 'category_id' => Category::where('name', 'Router Connectivity Issues')->first()->id, 'status' => 'open'],
            ['title' => 'Modem setup issue', 'description' => 'Modem fails to configure properly during the initial setup. The device does not recognize the internet signal from the service provider. Ensuring proper configuration is essential for establishing a stable internet connection.', 'user_id' => User::where('email', 'customer1@example.com')->first()->id, 'category_id' => Category::where('name', 'Modem Configuration Issues')->first()->id, 'status' => 'open'],
            ['title' => 'Modem not connecting', 'description' => 'Modem fails to establish a stable internet connection. The device frequently loses sync and requires a reboot. Investigating and resolving this issue will ensure uninterrupted internet access.', 'user_id' => User::where('email', 'customer2@example.com')->first()->id, 'category_id' => Category::where('name', 'Modem Connectivity Issues')->first()->id, 'status' => 'backlog'],
            ['title' => 'Virus detected on PC', 'description' => 'Antivirus software has detected a virus on the computer, causing performance issues and potential data loss. Immediate removal is necessary to prevent further damage and ensure data security.', 'user_id' => User::where('email', 'customer1@example.com')->first()->id, 'category_id' => Category::where('name', 'Virus and Malware Removal')->first()->id, 'status' => 'open'],
            ['title' => 'Data recovery needed', 'description' => 'Need to recover data from a damaged drive. The drive is no longer accessible and contains important files that must be retrieved. Utilizing data recovery techniques will help retrieve the lost data and prevent permanent data loss.', 'user_id' => User::where('email', 'customer2@example.com')->first()->id, 'category_id' => Category::where('name', 'Data Recovery Issues')->first()->id, 'status' => 'open'],
        ];

        foreach ($tickets as $ticket) {
            Ticket::create($ticket);
        }
    }
}
