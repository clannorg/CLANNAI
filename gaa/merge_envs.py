
import yaml

def merge_envs(file1, file2, output_file):
    with open(file1, 'r') as f:
        env1 = yaml.safe_load(f)
    with open(file2, 'r') as f:
        env2 = yaml.safe_load(f)

    # Merge channels
    channels = sorted(list(set(env1.get('channels', []) + env2.get('channels', []))))

    # Merge dependencies
    deps1 = env1.get('dependencies', [])
    deps2 = env2.get('dependencies', [])

    conda_deps1 = [dep for dep in deps1 if not isinstance(dep, dict)]
    conda_deps2 = [dep for dep in deps2 if not isinstance(dep, dict)]
    
    pip_deps1 = []
    pip_section1 = next((item for item in deps1 if isinstance(item, dict) and 'pip' in item), None)
    if pip_section1:
        pip_deps1 = pip_section1.get('pip', [])

    pip_deps2 = []
    pip_section2 = next((item for item in deps2 if isinstance(item, dict) and 'pip' in item), None)
    if pip_section2:
        pip_deps2 = pip_section2.get('pip', [])
        
    # Combine and remove duplicates
    combined_conda_deps = sorted(list(set(conda_deps1 + conda_deps2)))
    combined_pip_deps = sorted(list(set(pip_deps1 + pip_deps2)))

    # Assemble final dependencies list
    final_deps = combined_conda_deps
    if combined_pip_deps:
        final_deps.append({'pip': combined_pip_deps})
        
    # Create the new environment dictionary
    merged_env = {
        'name': 'gaa-pipeline',
        'channels': channels,
        'dependencies': final_deps
    }

    # Write the new environment file
    with open(output_file, 'w') as f:
        yaml.dump(merged_env, f, default_flow_style=False, sort_keys=False)

    print(f"Successfully merged environments into {output_file}")

if __name__ == "__main__":
    merge_envs('gaa-tracker.yml', 'ball.yml', 'combined_environment.yml') 