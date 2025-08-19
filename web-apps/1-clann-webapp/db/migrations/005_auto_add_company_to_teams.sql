-- Migration: Auto-add company users to new teams
-- This ensures company users are automatically added to any newly created team

-- Function to add all company users to a new team
CREATE OR REPLACE FUNCTION add_company_users_to_new_team()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert all company users into the new team
    INSERT INTO team_members (team_id, user_id)
    SELECT NEW.id, u.id
    FROM users u
    WHERE u.role = 'company'
    ON CONFLICT (team_id, user_id) DO NOTHING;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to run after a new team is created
CREATE TRIGGER auto_add_company_users_trigger
    AFTER INSERT ON teams
    FOR EACH ROW
    EXECUTE FUNCTION add_company_users_to_new_team();

-- Also create a function to add new company users to all existing teams
CREATE OR REPLACE FUNCTION add_new_company_user_to_all_teams()
RETURNS TRIGGER AS $$
BEGIN
    -- Only run if the new user is a company user
    IF NEW.role = 'company' THEN
        -- Add this company user to all existing teams
        INSERT INTO team_members (team_id, user_id)
        SELECT t.id, NEW.id
        FROM teams t
        ON CONFLICT (team_id, user_id) DO NOTHING;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to run after a new company user is created
CREATE TRIGGER auto_add_new_company_user_trigger
    AFTER INSERT ON users
    FOR EACH ROW
    EXECUTE FUNCTION add_new_company_user_to_all_teams();

-- Also handle role changes (if a user becomes company)
CREATE OR REPLACE FUNCTION handle_user_role_change()
RETURNS TRIGGER AS $$
BEGIN
    -- If user role changed to company, add them to all teams
    IF OLD.role != 'company' AND NEW.role = 'company' THEN
        INSERT INTO team_members (team_id, user_id)
        SELECT t.id, NEW.id
        FROM teams t
        ON CONFLICT (team_id, user_id) DO NOTHING;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for role changes
CREATE TRIGGER handle_user_role_change_trigger
    AFTER UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION handle_user_role_change();
