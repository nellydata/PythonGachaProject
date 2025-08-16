# Contributing to Nightmare Nexus

Thank you for your interest in contributing to Nightmare Nexus! This document provides guidelines for contributing to this horror-themed gacha collection game.

## 🎯 Project Overview

Nightmare Nexus is an educational Python project showcasing:
- Game development with Tkinter
- Object-oriented programming patterns
- JSON data management
- GUI design principles
- Game mechanics implementation

## 🤝 Ways to Contribute

### 🐛 Bug Reports
Use the in-game bug reporting system or GitHub Issues to report:
- Game crashes or errors
- UI/UX problems
- Balance issues
- Performance problems
- Save/load issues

**Bug Report Template:**
```
**Bug Description:**
Brief description of the issue

**Steps to Reproduce:**
1. Step one
2. Step two
3. Step three

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Environment:**
- OS: (Windows/Mac/Linux)
- Python Version: (e.g., 3.9.0)
- Game Version: (e.g., v1.2)
```

### 💡 Feature Requests
We welcome suggestions for:
- New horror entities
- Additional game modes
- UI/UX improvements
- Balance adjustments
- Quality of life features

### 🔧 Code Contributions

#### Getting Started
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

#### Code Style Guidelines
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings for new functions and classes
- Comment complex logic
- Maintain consistent indentation (4 spaces)

#### Example Code Style:
```python
def calculate_damage(self, attacker, defender):
    """
    Calculate damage between attacker and defender.
    
    Args:
        attacker (dict): Unit performing the attack
        defender (dict): Unit receiving the attack
        
    Returns:
        tuple: (damage_amount, is_critical_hit)
    """
    base_damage = attacker["attack"] - defender["defense"]
    is_crit = random.randint(1, 100) <= attacker["crit_rate"]
    
    if is_crit:
        damage = int(base_damage * (attacker["crit_damage"] / 100))
    else:
        damage = base_damage
        
    return max(1, damage), is_crit
```

### 🎨 Content Contributions

#### New Horror Entities
When suggesting new entities, provide:
- **Name**: Entity name
- **Origin**: Source material (Creepypasta, SCP, etc.)
- **Rarity**: Common/Rare/Epic/Legendary
- **Base Stats**: HP, Attack, Defense, Speed
- **Skill**: Description of special ability
- **Passive**: Ongoing effect description
- **Lore**: Brief background description

#### Example Entity Submission:
```python
{
    "name": "The Backrooms Entity",
    "rarity": "Epic",
    "hp": 120,
    "attack": 18,
    "defense": 8,
    "speed": 22,
    "skill": "reality_shift",
    "crit_rate": 10,
    "crit_damage": 175,
    "accuracy": 90,
    "evasion": 15,
    "passive": "Phase Walk: 25% chance to avoid all damage",
    "description": "A mysterious entity that stalks the endless yellow rooms."
}
```

## 📋 Development Setup

### Prerequisites
- Python 3.7 or higher
- tkinter (usually included with Python)
- Git for version control

### Local Development
```bash
# Clone your fork
git clone https://github.com/yourusername/nightmare-nexus.git
cd nightmare-nexus

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the game
python nightmare_nexus_v0.1.py
```

### Testing Your Changes
- Test all affected game modes
- Verify save/load functionality works
- Check UI responsiveness
- Test with different screen resolutions
- Verify no Python errors in console

## 🎮 Game Design Principles

### Balance Guidelines
- Common units: Basic stats, simple abilities
- Rare units: Moderate stats, useful abilities
- Epic units: High stats, powerful abilities
- Legendary units: Exceptional stats, unique mechanics

### UI/UX Guidelines
- Maintain dark horror theme
- Use clear, readable fonts
- Provide visual feedback for actions
- Keep navigation intuitive
- Ensure accessibility

### Performance Guidelines
- Minimize memory usage
- Avoid blocking the UI thread
- Optimize battle calculations
- Handle large save files gracefully

## 🔍 Review Process

### Pull Request Guidelines
1. **Clear Title**: Describe what the PR does
2. **Detailed Description**: Explain changes and motivation
3. **Testing**: Describe how you tested the changes
4. **Screenshots**: Include UI changes if applicable
5. **Breaking Changes**: Note any compatibility issues

### Review Criteria
- Code quality and style
- Functionality and testing
- Performance impact
- User experience
- Documentation updates

## 📚 Resources

### Learning Resources
- [Python Official Documentation](https://docs.python.org/3/)
- [Tkinter Tutorial](https://docs.python.org/3/library/tkinter.html)
- [PEP 8 Style Guide](https://pep8.org/)
- [Git Handbook](https://guides.github.com/introduction/git-handbook/)

### Game Design References
- Horror game mechanics
- Gacha game design principles
- Turn-based combat systems
- RPG progression mechanics

## 🏆 Recognition

Contributors will be recognized in:
- Game credits (About section)
- README contributors list
- Release notes for major contributions

## 📞 Questions?

- Open a GitHub Issue for public discussion
- Check existing issues and pull requests first
- Be patient and respectful in communications

## 📜 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the project's educational goals
- Respect intellectual property rights
- Keep content appropriate for the horror theme

---

Thank you for helping make Nightmare Nexus even more terrifying! 👻

*Remember: Every great horror story starts with someone brave enough to open the door...*
