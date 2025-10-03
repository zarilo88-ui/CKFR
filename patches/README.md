# Patch Usage

This directory contains patch files that can be applied to reproduce prior optimisation work.

## Available patches

- `refine_ship_allocation.patch`: captures commit `9fda9ed` ("Refine ship allocation flows and polish UI").

## Applying the patch

From the repository root run either of the following commands:

```bash
git apply patches/refine_ship_allocation.patch
```

or, to preserve the original commit metadata:

```bash
git am patches/refine_ship_allocation.patch
```

After applying, review the changes and run the test suite:

```bash
python manage.py test
```
