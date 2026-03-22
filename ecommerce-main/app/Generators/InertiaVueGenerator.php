<?php

namespace App\Generators;

use Blueprint\Contracts\Generator;
use Blueprint\Models\Model;
use Blueprint\Tree;
use Illuminate\Filesystem\Filesystem;
use Illuminate\Support\Str;

class InertiaVueGenerator implements Generator
{
    protected $filesystem;

    protected $stubPath;

    public function __construct(Filesystem $filesystem)
    {
        $this->filesystem = $filesystem;
        $this->stubPath = \base_path('stubs/custom');
    }

    public function types(): array
    {
        return ['inertia_vue'];
    }

    public function output(Tree $tree): array
    {
        $output = [];

        $models = $tree->models();

        if (empty($models)) {
            return $output;
        }

        foreach ($models as $model) {
            $paths = $this->generateForModel($model);
            if (! empty($paths)) {
                $output = array_merge($output, $paths);
            }
        }

        return $output;
    }

    protected function generateForModel(Model $model): array
    {
        $output = [];

        // Generate Vue components
        $output = array_merge($output, $this->generateCrud($model));

        // $output = array_merge($output, $this->generateIndex($model));
        // $output = array_merge($output, $this->generateCreate($model));
        // $output = array_merge($output, $this->generateEdit($model));
        // $output = array_merge($output, $this->generateShow($model));
        $output = array_merge($output, $this->generateForm($model));

        return $output;
    }

    protected function generateCrud(Model $model): array
    {
        // $modelPlural = Str::plural($model->name());
        $path = $this->getVueComponentPath($model, 'Index');

        if (! $this->filesystem->exists(dirname($path))) {
            $this->filesystem->makeDirectory(dirname($path), 0755, true);
        }

        $this->filesystem->put(
            $path,
            $this->compileStub('crud', [
                '{{ ModelName }}' => $model->name(),
                '{{ modelName }}' => Str::camel($model->name()),
                '{{ modelVariablePlural }}' => Str::plural(Str::camel($model->name())),
                '{{ modelRouteName }}' => Str::kebab(Str::plural($model->name())),
                '{{ modelFields }}' => $this->getFieldsForCrudIndex($model),
            ])
        );

        return [$path];
    }

    protected function generateIndex(Model $model): array
    {
        $path = $this->getVueComponentPath($model, 'Index');

        if (! $this->filesystem->exists(dirname($path))) {
            $this->filesystem->makeDirectory(dirname($path), 0755, true);
        }

        $this->filesystem->put(
            $path,
            $this->compileStub('index', [
                '{{ ModelName }}' => $model->name(),
                '{{ modelName }}' => Str::camel($model->name()),
                '{{ modelVariablePlural }}' => Str::plural(Str::camel($model->name())),
                '{{ modelRouteName }}' => Str::kebab(Str::plural($model->name())),
                '{{ modelFields }}' => $this->getFieldsForIndex($model),
            ])
        );

        return [$path];
    }

    protected function generateCreate(Model $model): array
    {
        $path = $this->getVueComponentPath($model, 'Create');

        if (! $this->filesystem->exists(dirname($path))) {
            $this->filesystem->makeDirectory(dirname($path), 0755, true);
        }

        $this->filesystem->put(
            $path,
            $this->compileStub('create', [
                '{{ ModelName }}' => $model->name(),
                '{{ modelName }}' => Str::camel($model->name()),
                '{{ modelRouteName }}' => Str::kebab(Str::plural($model->name())),
            ])
        );

        return [$path];
    }

    protected function generateEdit(Model $model): array
    {
        $path = $this->getVueComponentPath($model, 'Edit');

        if (! $this->filesystem->exists(dirname($path))) {
            $this->filesystem->makeDirectory(dirname($path), 0755, true);
        }

        $this->filesystem->put(
            $path,
            $this->compileStub('edit', [
                '{{ ModelName }}' => $model->name(),
                '{{ modelName }}' => Str::camel($model->name()),
                '{{ modelRouteName }}' => Str::kebab(Str::plural($model->name())),
            ])
        );

        return [$path];
    }

    protected function generateShow(Model $model): array
    {
        $path = $this->getVueComponentPath($model, 'Show');

        if (! $this->filesystem->exists(dirname($path))) {
            $this->filesystem->makeDirectory(dirname($path), 0755, true);
        }

        $this->filesystem->put(
            $path,
            $this->compileStub('show', [
                '{{ ModelName }}' => $model->name(),
                '{{ modelName }}' => Str::camel($model->name()),
                '{{ modelRouteName }}' => Str::kebab(Str::plural($model->name())),
                '{{ modelFields }}' => $this->getFieldsForShow($model),
            ])
        );

        return [$path];
    }

    protected function generateForm(Model $model): array
    {
        $path = $this->getVueComponentPath($model, 'Form');

        if (! $this->filesystem->exists(dirname($path))) {
            $this->filesystem->makeDirectory(dirname($path), 0755, true);
        }

        $this->filesystem->put(
            $path,
            $this->compileStub('form', [
                '{{ ModelName }}' => $model->name(),
                '{{ modelName }}' => Str::camel($model->name()),
                '{{ formFields }}' => $this->getFormFields($model),
            ])
        );

        return [$path];
    }

    protected function getVueComponentPath(Model $model, string $type): string
    {
        $modelPlural = Str::plural($model->name());

        return resource_path('js/Pages/'.$modelPlural.'/'.$type.'.vue');
    }

    protected function compileStub(string $stubName, array $replacements = []): string
    {
        $stub = $this->filesystem->get("{$this->stubPath}/{$stubName}.stub");

        foreach ($replacements as $search => $replace) {
            $stub = str_replace($search, $replace, $stub);
        }

        return $stub;
    }

    protected function getFieldsForCrudIndex(Model $model): string
    {
        $fields = [];

        foreach ($model->columns() as $column) {
            if (in_array($column->name(), ['id', 'password', 'remember_token', 'deleted_at'])) {
                continue;
            }
            $fields[] = $column->name().": '',";
        }

        return implode("\n    ", $fields);
    }

    protected function getFieldsForIndex(Model $model): string
    {
        $fields = [];

        foreach ($model->columns() as $column) {
            // Skip common fields we don't typically show in index
            if (in_array($column->name(), ['id', 'password', 'remember_token', 'created_at', 'updated_at', 'deleted_at'])) {
                continue;
            }

            $fields[] = "        <td class=\"px-6 py-4 whitespace-nowrap\">{{ {$column->name()} }}</td>";
        }

        return implode("\n", $fields);
    }

    protected function getFieldsForShow(Model $model): string
    {
        $fields = [];

        foreach ($model->columns() as $column) {
            // Skip common fields we don't typically show individually
            if (in_array($column->name(), ['password', 'remember_token'])) {
                continue;
            }

            $label = Str::title(str_replace('_', ' ', $column->name()));

            $fields[] = "        <div class=\"mb-4\">\n".
                "            <h3 class=\"text-lg font-medium\">{$label}:</h3>\n".
                '            <p>{{ '.Str::camel($model->name()).".{$column->name()} }}</p>\n".
                '        </div>';
        }

        return implode("\n\n", $fields);
    }

    protected function getFormFields(Model $model): string
    {
        $fields = [];

        foreach ($model->columns() as $column) {
            // Skip fields that shouldn't be in forms
            if (in_array($column->name(), ['id', 'created_at', 'updated_at', 'deleted_at'])) {
                continue;
            }

            $label = Str::title(str_replace('_', ' ', $column->name()));
            $name = $column->name();
            $modelVariable = Str::camel($model->name());

            // Use different PrimeVue (or privevue) components based on column type and name
            if ($name === 'password') {
                $fields[] = "    <div class=\"mb-4\">
        <label for=\"{$name}\" class=\"\">{$label}</label>
        <Password id=\"{$name}\" v-model=\"form.{$name}\" class=\"mt-1 block w-full\" />
        <div v-if=\"form?.errors?.{$name}\" class=\"text-red-500 text-sm mt-1\">{{ form?.errors?.{$name} }}</div>
    </div>";
            } elseif (str_contains($column->dataType(), 'text')) {
                $fields[] = "    <div class=\"mb-4\">
        <label for=\"{$name}\" class=\"\">{$label}</label>
        <InputTextarea id=\"{$name}\" v-model=\"form.{$name}\" class=\"mt-1 block w-full\" rows=\"3\" />
        <div v-if=\"form?.errors?.{$name}\" class=\"text-red-500 text-sm mt-1\">{{ form?.errors?.{$name} }}</div>
    </div>";
            } elseif (str_contains($column->dataType(), 'boolean')) {
                $fields[] = "    <div class=\"mb-4\">
        <div class=\"flex items-center\">
            <Checkbox id=\"{$name}\" v-model=\"form.{$name}\" class=\"h-4 w-4\" binary />
            <label for=\"{$name}\" class=\"ml-2 \">{$label}</label>
        </div>
        <div v-if=\"form?.errors?.{$name}\" class=\"text-red-500 text-sm mt-1\">{{ form?.errors?.{$name} }}</div>
    </div>";
            } elseif (
                str_contains($column->dataType(), 'int')
                || str_contains($column->dataType(), 'decimal')
                || str_contains($column->dataType(), 'float')
            ) {
                $fields[] = "    <div class=\"mb-4\">
        <label for=\"{$name}\" class=\"\">{$label}</label>
        <InputNumber id=\"{$name}\" v-model=\"form.{$name}\" class=\"mt-1 block w-full\" />
        <div v-if=\"form?.errors?.{$name}\" class=\"text-red-500 text-sm mt-1\">{{ form?.errors?.{$name} }}</div>
    </div>";
            } elseif (
                str_contains($column->dataType(), 'date')
                || str_contains($column->dataType(), 'time')
                || str_contains($column->dataType(), 'datetime')
            ) {
                $fields[] = "    <div class=\"mb-4\">
        <label for=\"{$name}\" class=\"\">{$label}</label>
        <Calendar id=\"{$name}\" v-model=\"form.{$name}\" class=\"mt-1 block w-full\" />
        <div v-if=\"form?.errors?.{$name}\" class=\"text-red-500 text-sm mt-1\">{{ form?.errors?.{$name} }}</div>
    </div>";
            } elseif ($name === 'email') {
                $fields[] = "    <div class=\"mb-4\">
        <label for=\"{$name}\" class=\"\">{$label}</label>
        <InputText id=\"{$name}\" v-model=\"form.{$name}\" type=\"email\" class=\"mt-1 block w-full\" />
        <div v-if=\"form?.errors?.{$name}\" class=\"text-red-500 text-sm mt-1\">{{ form?.errors?.{$name} }}</div>
    </div>";
            } elseif (str_contains($column->dataType(), 'file')) {
                $fields[] = "    <div class=\"mb-4\">
        <label for=\"{$name}\" class=\"\">{$label}</label>
        <FileUpload id=\"{$name}\" v-model=\"form.{$name}\" class=\"mt-1 block w-full\" />
        <div v-if=\"form?.errors?.{$name}\" class=\"text-red-500 text-sm mt-1\">{{ form?.errors?.{$name} }}</div>
    </div>";
            } else {
                $fields[] = "    <div class=\"mb-4\">
        <label for=\"{$name}\" class=\"\">{$label}</label>
        <InputText id=\"{$name}\" v-model=\"form.{$name}\" class=\"mt-1 block w-full\" />
        <div v-if=\"form?.errors?.{$name}\" class=\"text-red-500 text-sm mt-1\">{{ form?.errors?.{$name} }}</div>
    </div>";
            }
        }

        return implode("\n\n", $fields);
    }

    protected function getFormFields2(Model $model): string
    {
        $fields = [];

        foreach ($model->columns() as $column) {
            // Skip fields that shouldn't be in forms
            if (in_array($column->name(), ['id', 'created_at', 'updated_at', 'deleted_at'])) {
                continue;
            }

            $label = Str::title(str_replace('_', ' ', $column->name()));
            $name = $column->name();
            $modelVariable = Str::camel($model->name());

            // Handle different field types
            if ($name === 'password') {
                $fields[] = "    <div class=\"mb-4\">\n".
                    "        <label for=\"{$name}\" class=\"block text-sm font-medium text-gray-700\">{$label}</label>\n".
                    "        <input type=\"password\" id=\"{$name}\" v-model=\"form.{$name}\" class=\"mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500\" />\n".
                    "        <div v-if=\"form?.errors?.{$name}\" class=\"text-red-500 text-sm mt-1\">{{ form?.errors?.{$name} }}</div>\n".
                    '    </div>';
            } elseif (str_contains($column->dataType(), 'text')) {
                $fields[] = "    <div class=\"mb-4\">\n".
                    "        <label for=\"{$name}\" class=\"block text-sm font-medium text-gray-700\">{$label}</label>\n".
                    "        <textarea id=\"{$name}\" v-model=\"form.{$name}\" class=\"mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500\" rows=\"3\"></textarea>\n".
                    "        <div v-if=\"form?.errors?.{$name}\" class=\"text-red-500 text-sm mt-1\">{{ form?.errors?.{$name} }}</div>\n".
                    '    </div>';
            } elseif (str_contains($column->dataType(), 'boolean')) {
                $fields[] = "    <div class=\"mb-4\">\n".
                    "        <div class=\"flex items-center\">\n".
                    "            <input type=\"checkbox\" id=\"{$name}\" v-model=\"form.{$name}\" class=\"h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500\" />\n".
                    "            <label for=\"{$name}\" class=\"ml-2 block text-sm font-medium text-gray-700\">{$label}</label>\n".
                    "        </div>\n".
                    "        <div v-if=\"form?.errors?.{$name}\" class=\"text-red-500 text-sm mt-1\">{{ form?.errors?.{$name} }}</div>\n".
                    '    </div>';
            } else {
                $fields[] = "    <div class=\"mb-4\">\n".
                    "        <label for=\"{$name}\" class=\"block text-sm font-medium text-gray-700\">{$label}</label>\n".
                    "        <input type=\"text\" id=\"{$name}\" v-model=\"form.{$name}\" class=\"mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500\" />\n".
                    "        <div v-if=\"form?.errors?.{$name}\" class=\"text-red-500 text-sm mt-1\">{{ form?.errors?.{$name} }}</div>\n".
                    '    </div>';
            }
        }

        return implode("\n\n", $fields);
    }
}
