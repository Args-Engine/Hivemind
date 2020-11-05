ocal p = premake

local tree = p.tree
local project = p.project
local config = p.config

p.modules.hivemind = {}
p.modules.hivemind._VERSION = p._VERSION

local hivemind = p.modules.hivemind

hivemind.project = {}
hivemind.project.elements = {}

local function ends_with(str, ending)
	return ending == "" or str:sub(-#ending) == ending
end

local compiler = 'vs-cxx'
local cxxflags = {}

--generate commands like RUN CXX /P <file>.cpp CXXFLAGS INCLUDES
function hivemind.project.preprocess(prj)
	local filetree = project.getsourcetree(prj)

	tree.traverse(filetree, {
		onleaf = function(node)
			if ends_with(node.path,'.c')
				or ends_with(node.path,'.cpp')
				or ends_with(node.path,'.cxx')
			then

				print("Generating preprocess commands for: " .. node.path)
				_p('RUN '..compiler..table.concat(cxxflags,' ')..' /Wall /Fo %s /OUT:%s',node.path,node.name..'.i')
			end
		end
	})

	_p('WAIT')
end

--generate commands like RUN CXX /Wall /Fo <file>.obj <file>.i
function hivemind.project.compile(prj)

	local filetree = project.getsourcetree(prj)

	tree.traverse(filetree, {
		onleaf = function(node)
			if ends_with(node.path,'.c')
				or ends_with(node.path,'.cpp')
				or ends_with(node.path,'.cxx')
			then

				print("Generating compile commands for : " ..  node.path)
				-- path = string.gsub(node.path,"%.cpp|%.c|%.cxx",".i")
				_p('RUN '..compiler..table.concat(cxxflags,' ')..' /Wall /Fo %s /OUT:%s',node.name..'.i',node.name..'.obj')
			end
		end
	})

	_p('WAIT')
end

--generate commands like RUN LINK <files...>.obj <output>.exe
function hivemind.project.link(prj)

	local filetree = project.getsourcetree(prj)
	local to_link =""

	local outpath = p.filename(prj, ".lib")
	outpath = path.getrelative(prj.workspace.location, outpath)

	tree.traverse(filetree, {
		onleaf = function(node)
			if ends_with(node.path,'.c')
				or ends_with(node.path,'.cpp')
				or ends_with(node.path,'.cxx')
			then
				to_link = to_link .. ' ' .. node.name ..'.obj'
			end
		end
	})

	_p("RUN vs-link %s",to_link .. " /OUT:" ..outpath)
	_p("WAIT")
end

hivemind.project.elements.project = function(prj)
	return {
		hivemind.project.preprocess,
		hivemind.project.compile,
		hivemind.project.link
	}
end

function hivemind.project.generate(prj)
	p.utf8()

	p.callArray(hivemind.project.elements.project,prj)
end

function hivemind.esc(value)
	return value
end

function hivemind.__fake(_)
	_p('WAIT')
end

-- Hivemind does not really have the notion of "Workspaces" for all projects
-- Might add that feature later
function hivemind.generateWorkspace(wks)
	p.eol("\r\n")
	p.indent("  ")
	p.escaper(hivemind.esc)
	p.generate(wks, ".hivemind", hivemind.__fake)

end

function hivemind.generateProject(prj)
	p.eol("\r\n")
	p.indent("  ")
	p.escaper(hivemind.esc)

	if project.isc(prj) or project.iscpp(prj) then
		p.generate(prj,".hivemind",hivemind.project.generate)
	end
end

function hivemind.cleanWorkspace(wks)

end

function hivemind.cleanProject(prj)

end

function hivemind.cleanTarget(prj)

end


return hivemind
