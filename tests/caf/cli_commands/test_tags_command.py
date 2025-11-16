from pathlib import Path

from libcaf.repository import Repository
from pytest import CaptureFixture

from caf import cli_commands


def test_tags_command_empty(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.tags(working_dir_path=temp_repo.working_dir) == 0
    
    output = capsys.readouterr().out
    assert 'No tags found' in output


def test_tags_command_single(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    # Create a commit and tag
    temp_file = temp_repo.working_dir / 'test_file.txt'
    temp_file.write_text('Test content')
    commit_ref = temp_repo.commit_working_dir('Author', 'Test commit')
    
    tag_name = 'v1.0.0'
    temp_repo.create_tag(tag_name, commit_ref)
    
    assert cli_commands.tags(working_dir_path=temp_repo.working_dir) == 0
    
    output = capsys.readouterr().out
    assert 'Tags:' in output
    assert tag_name in output


def test_tags_command_multiple(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    # Create commits and multiple tags
    temp_file = temp_repo.working_dir / 'test_file.txt'
    temp_file.write_text('Test content')
    commit_ref1 = temp_repo.commit_working_dir('Author', 'First commit')
    
    temp_file.write_text('Updated content')
    commit_ref2 = temp_repo.commit_working_dir('Author', 'Second commit')
    
    tag_names = ['v1.0.0', 'v1.1.0', 'v2.0.0']
    temp_repo.create_tag(tag_names[0], commit_ref1)
    temp_repo.create_tag(tag_names[1], commit_ref1)
    temp_repo.create_tag(tag_names[2], commit_ref2)
    
    assert cli_commands.tags(working_dir_path=temp_repo.working_dir) == 0
    
    output = capsys.readouterr().out
    assert 'Tags:' in output
    for tag_name in tag_names:
        assert tag_name in output


def test_tags_command_after_delete(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    # Create commits and tags
    temp_file = temp_repo.working_dir / 'test_file.txt'
    temp_file.write_text('Test content')
    commit_ref = temp_repo.commit_working_dir('Author', 'Test commit')
    
    tag_names = ['v1.0.0', 'v1.1.0', 'v2.0.0']
    for tag_name in tag_names:
        temp_repo.create_tag(tag_name, commit_ref)
    
    # Delete one tag
    temp_repo.delete_tag(tag_names[1])
    
    assert cli_commands.tags(working_dir_path=temp_repo.working_dir) == 0
    
    output = capsys.readouterr().out
    assert 'Tags:' in output
    assert tag_names[0] in output
    assert tag_names[1] not in output
    assert tag_names[2] in output


def test_tags_command_no_repo(temp_repo_dir: Path, capsys: CaptureFixture[str]) -> None:
    # tags() doesn't require repo to exist, it just returns empty list
    assert cli_commands.tags(working_dir_path=temp_repo_dir) == 0
    
    assert 'No tags found' in capsys.readouterr().out


def test_tags_command_output_format(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    # Create a commit and tag
    temp_file = temp_repo.working_dir / 'test_file.txt'
    temp_file.write_text('Test content')
    commit_ref = temp_repo.commit_working_dir('Author', 'Test commit')
    
    tag_name = 'v1.0.0'
    temp_repo.create_tag(tag_name, commit_ref)
    
    assert cli_commands.tags(working_dir_path=temp_repo.working_dir) == 0
    
    output = capsys.readouterr().out
    lines = output.splitlines()
    
    # Should have "Tags:" header and the tag name
    assert len(lines) >= 2
    assert 'Tags:' in lines[0] or 'Tags:' in output
    assert tag_name in output


