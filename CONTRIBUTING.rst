Contributing
============

When developing use the following guidelines:


Workflow
--------

1. Create a development branch
2. Make changes to the source
3. Add unit tests to test your changes
4. Document any changes in `docs/` - we use Sphinx in this module
5. Apply formatting and linting checks - see tools below
6. Create a merge request once changes are ready for production
7. Ensure CI pipeline succeeds
8. Update CHANGELOG.rst with any notable changes or fixes
9. Once reviewed and happy, apply merge request with squashed commits
10. For a release, update `VERSION.txt` and create and push corresponding tag
11. Check wheel is uploaded to package registry or release package is created
    as appropriate


Tools
-----

1. Validate linting using ruff: `uv run ruff check`
2. Fix basic issues with linting: `uv run ruff check --fix`
3. Format code using ruff: `uv run ruff format `
4. Validate type hints using mypy: `uv run mypy`
5. Build and check documentation using Sphinx: `uv run poe docs`
6. Maintain coverage using coverage module: `uv run pytest` and `uv run poe cov`


Deployment
----------

The CI/CD server will build a deployment package and upload it to the package registry on GitLab
whenever a tag is pushed.

It will also produce a release on GitLab with link(s) to the package registry.
