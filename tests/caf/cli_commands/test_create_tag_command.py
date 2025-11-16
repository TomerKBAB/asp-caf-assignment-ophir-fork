from pathlib import Path

from libcaf.constants import DEFAULT_REPO_DIR, REFS_DIR, TAGS_DIR
from libcaf.repository import Repository
from pytest import CaptureFixture

from caf import cli_commands


def test_create_tag_command(temp_repo: Repository) -> None:
    # Create a commit first
    temp_file = temp_repo.working_dir / 'test_file.txt'
    temp_file.write_text('Test content')
    commit_ref = temp_repo.commit_working_dir('Author', 'Test commit')
    
    # Create a tag via CLI
    assert cli_commands.create_tag(
        working_dir_path=temp_repo.working_dir,
        **{'tag name': 'v1.0.0', 'ref': commit_ref}
    ) == 0
    
    tag_path = temp_repo.working_dir / DEFAULT_REPO_DIR / REFS_DIR / TAGS_DIR / 'v1.0.0'
    assert tag_path.exists()


def test_create_tag_with_head_ref(temp_repo: Repository) -> None:
    # Create a commit first
    temp_file = temp_repo.working_dir / 'test_file.txt'
    temp_file.write_text('Test content')
    temp_repo.commit_working_dir('Author', 'Test commit')
    
    # Create a tag using HEAD reference
    assert cli_commands.create_tag(
        working_dir_path=temp_repo.working_dir,
        **{'tag name': 'v1.0.0', 'ref': 'HEAD'}
    ) == 0
    
    tag_path = temp_repo.working_dir / DEFAULT_REPO_DIR / REFS_DIR / TAGS_DIR / 'v1.0.0'
    assert tag_path.exists()


def test_create_tag_missing_name(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    temp_file = temp_repo.working_dir / 'test_file.txt'
    temp_file.write_text('Test content')
    commit_ref = temp_repo.commit_working_dir('Author', 'Test commit')
    
    assert cli_commands.create_tag(
        working_dir_path=temp_repo.working_dir,
        **{'ref': commit_ref}
    ) == -1
    
    assert 'Tag name is required' in capsys.readouterr().err


def test_create_tag_missing_ref(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.create_tag(
        working_dir_path=temp_repo.working_dir,
        **{'tag name': 'v1.0.0'}
    ) == -1
    
    output = capsys.readouterr().err
    assert 'ref is required' in output


def test_create_tag_duplicate(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    temp_file = temp_repo.working_dir / 'test_file.txt'
    temp_file.write_text('Test content')
    commit_ref = temp_repo.commit_working_dir('Author', 'Test commit')
    
    # Create first tag
    assert cli_commands.create_tag(
        working_dir_path=temp_repo.working_dir,
        **{'tag name': 'v1.0.0', 'ref': commit_ref}
    ) == 0
    
    capsys.readouterr()
    
    # Try to create duplicate tag
    assert cli_commands.create_tag(
        working_dir_path=temp_repo.working_dir,
        **{'tag name': 'v1.0.0', 'ref': commit_ref}
    ) == -1
    
    assert 'already exists' in capsys.readouterr().err


def test_create_tag_invalid_ref(temp_repo: Repository) -> None:
    # RefError is not caught by CLI, so it propagates as an exception
    from libcaf.ref import RefError
    from pytest import raises
    
    with raises(RefError, match='Invalid reference'):
        cli_commands.create_tag(
            working_dir_path=temp_repo.working_dir,
            **{'tag name': 'v1.0.0', 'ref': 'invalid_ref_12345'}
        )


def test_create_tag_no_repo(temp_repo_dir: Path, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.create_tag(
        working_dir_path=temp_repo_dir,
        **{'tag name': 'v1.0.0', 'ref': 'a' * 40}
    ) == -1
    
    assert 'No repository found at' in capsys.readouterr().err


def test_create_tag_success_message(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    temp_file = temp_repo.working_dir / 'test_file.txt'
    temp_file.write_text('Test content')
    commit_ref = temp_repo.commit_working_dir('Author', 'Test commit')
    
    assert cli_commands.create_tag(
        working_dir_path=temp_repo.working_dir,
        **{'tag name': 'v1.0.0', 'ref': commit_ref}
    ) == 0
    
    output = capsys.readouterr().out
    assert 'Tag "v1.0.0" created' in output
    assert commit_ref in output


