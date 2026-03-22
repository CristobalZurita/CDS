<?php

namespace App\Exports;

use App\Models\Todo;
use Carbon\Carbon;
use Maatwebsite\Excel\Concerns\FromCollection;
use Maatwebsite\Excel\Concerns\ShouldAutoSize;
use Maatwebsite\Excel\Concerns\WithHeadings;
use Maatwebsite\Excel\Concerns\WithMapping;

class TodoExport implements FromCollection, ShouldAutoSize, WithHeadings, WithMapping
{
    protected $search;

    public function __construct($search = null)
    {
        $this->search = $search;
    }

    /**
     * @return \Illuminate\Support\Collection
     */
    public function collection()
    {
        return Todo::query()
            ->when($this->search, function ($query, $search) {
                $query->where(function ($q) use ($search) {
                    $q->where('title', 'like', "%{$search}%");
                });
            })
            ->get();
    }

    public function headings(): array
    {
        return [
            'ID',
            'Title',
            'Is Completed',
            'Created At',
            'Updated At',
        ];
    }

    public function map($todo): array
    {
        return [
            $todo->id,
            $todo->title,
            $todo->is_completed ? 'Yes' : 'No',
            Carbon::parse($todo->created_at)->format('Y-m-d H:i:s'),
            Carbon::parse($todo->updated_at)->format('Y-m-d H:i:s'),
        ];
    }
}
