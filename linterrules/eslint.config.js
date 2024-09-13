import { FlatCompat } from '@eslint/eslintrc';
import eslintRecommended from 'eslint/conf/eslint-recommended';
import prettierRecommended from 'eslint-plugin-prettier/recommended';

const compat = new FlatCompat();

export default [
    ...compat.extends('eslint:recommended'),
    ...compat.extends('plugin:prettier/recommended'),
    {
        rules: {
            'prettier/prettier': [
                'error',
                {
                    trailingComma: 'es5',
                    useTab: true,
                    tabWidth: 4,
                    semi: true,
                    singleQuote: true,
                    printWidth: 100,
                },
            ],
            'no-multiple-empty-lines': ['error', { max: 2, maxEOF: 1 }],
        },
    },
];