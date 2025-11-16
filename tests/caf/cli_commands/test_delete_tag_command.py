from pathlib import Path

from libcaf.constants import DEFAULT_REPO_DIR, REFS_DIR, TAGS_DIR
from libcaf.repository import Repository
from pytest import CaptureFixture

from caf import cli_commands


def test_delete_tag_command(temp_repo: Repository) -> None:
    # Create a commit and tag first
    temp_file = temp_repo.working_dir / 'test_file.txt'
    temp_file.write_text('Test content')
    commit_ref = temp_repo.commit_working_dir('Author', 'Test commit')
    
    tag_name = 'v1.0.0'
    temp_repo.create_tag(tag_name, commit_ref)
    
    tag_path = temp_repo.working_dir / DEFAULT_REPO_DIR / REFS_DIR / TAGS_DIR / tag_name
    assert tag_path.exists()
    
    # Delete the tag via CLI
    assert cli_commands.delete_tag(
        working_dir_path=temp_repo.working_dir,
        **{'tag name': tag_name}
    ) == 0
    
    assert not tag_path.exists()


def test_delete_tag_missing_name(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.delete_tag(
        working_dir_path=temp_repo.working_dir
    ) == -1
    
    assert 'Tag name is required' in capsys.readouterr().err


def test_delete_tag_nonexistent(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.delete_tag(
        working_dir_path=temp_repo.working_dir,
        **{'tag name': 'nonexistent_tag'}
    ) == -1
    
    assert 'does not exist' in capsys.readouterr().err


def test_delete_tag_no_repo(temp_repo_dir: Path, capsys: CaptureFixture[str]) -> None:
    # delete_tag doesn't have @requires_repo, so it raises RepositoryError, not RepositoryNotFoundError
    assert cli_commands.delete_tag(
        working_dir_path=temp_repo_dir,
        **{'tag name': 'v1.0.0'}
    ) == -1
    
    output = capsys.readouterr().err
    assert 'Repository error' in output
    assert 'does not exist' in output


def test_delete_tag_success_message(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    # Create a commit and tag first
    temp_file = temp_repo.working_dir / 'test_file.txt'
    temp_file.write_text('Test content')
    commit_ref = temp_repo.commit_working_dir('Author', 'Test commit')
    
    tag_name = 'v1.0.0'
    temp_repo.create_tag(tag_name, commit_ref)
    
    assert cli_commands.delete_tag(
        working_dir_path=temp_repo.working_dir,
        **{'tag name': tag_name}
    ) == 0
    
    output = capsys.readouterr().out
    assert f'Tag "{tag_name}" deleted successfully' in output


