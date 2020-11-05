local p = premake

newaction
{
	trigger 		= "hivemind",
	shortname 		= "Hivemind Distributed Compile",
	description 	= "Generate Hivemind Distributed Compile Commands",
	toolset 		= "msc-v142",

	valid_kinds     = { "ConsoleApp", "StaticLib", "SharedLib" },
	valid_languages = { "C", "C++"},
	valid_tools     = {
		cc     = { "msc" },
	},


	onWorkspace = function(wks)
		p.modules.hivemind.generateWorkspace(wks)
	end,
	onProject = function(prj)
		p.modules.hivemind.generateProject(prj)
	end,

	onCleanWorkspace = function(wks)
		p.modules.hivemind.cleanWorkspace(wks)
	end,
	onCleanProject = function(prj)
		p.modules.hivemind.cleanProject(prj)
	end,
	onCleanTarget = function(prj)
		p.modules.hivemind.cleanTarget(prj)
	end,
}


return function(cfg)
	return (_ACTION == "hivemind")
end
