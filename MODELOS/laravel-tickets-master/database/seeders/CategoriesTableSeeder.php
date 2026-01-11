<?php

namespace Database\Seeders;

use App\Models\Category;
use Illuminate\Database\Seeder;

class CategoriesTableSeeder extends Seeder {
    public function run(): void {
        $categories = [
            ['name' => 'Computer Hardware Issues', 'description' => 'Issues related to computer hardware like RAM, HDD, motherboard, etc.'],
            ['name' => 'Computer Software Issues', 'description' => 'Issues related to computer software like operating system, applications, etc.'],
            ['name' => 'Printer Connectivity Issues', 'description' => 'Issues related to printer connections and driver installations.'],
            ['name' => 'Printer Paper Jams', 'description' => 'Issues related to paper jams and printer hardware malfunctions.'],
            ['name' => 'Router Configuration Issues', 'description' => 'Issues related to router setup and configuration.'],
            ['name' => 'Router Connectivity Issues', 'description' => 'Issues related to router connections and network stability.'],
            ['name' => 'Modem Configuration Issues', 'description' => 'Issues related to modem setup and configuration.'],
            ['name' => 'Modem Connectivity Issues', 'description' => 'Issues related to modem connections and network stability.'],
            ['name' => 'Virus and Malware Removal', 'description' => 'Issues related to virus, malware, and other security threats.'],
            ['name' => 'Data Recovery Issues', 'description' => 'Issues related to data recovery from corrupted or damaged storage devices.'],
        ];

        foreach ($categories as $category) {
            Category::create($category);
        }
    }
}
