# GitBags

A GitBag is a [Bag](https://tools.ietf.org/html/draft-kunze-bagit-05) that is contained within a Git repository. For example, for a Bag within a directory named 'mybagdir,' you have this:

```
mybagdir/
├── bag-info.txt
├── bagit.txt
├── data
│   ├── file1.txt
│   └── file2.txt
├── manifest-md5.txt
└── tagmanifest-md5.txt
```
By converting the Bag to a GitBag (i.e., by initializing a Git repo within the Bag directory), you get this:

```
mybagdir/
├── bag-info.txt
├── bagit.txt
├── data
│   ├── file1.txt
│   └── file2.txt
├── .git
│   ├── branches
│   ├── config
│   ├── description
│   ├── HEAD
│   ├── hooks
│   │   ├── applypatch-msg.sample
│   │   ├── commit-msg.sample
│   │   ├── post-update.sample
│   │   ├── pre-applypatch.sample
│   │   ├── pre-commit.sample
│   │   ├── prepare-commit-msg.sample
│   │   ├── pre-push.sample
│   │   ├── pre-rebase.sample
│   │   └── update.sample
│   ├── info
│   │   └── exclude
│   ├── objects
│   │   ├── info
│   │   └── pack
│   └── refs
│       ├── heads
│       └── tags
├── manifest-md5.txt
└── tagmanifest-md5.txt
```

## Why would you do this?

Several potential reasons:

1. you want to record all changes to the content of a Bag
1. you get a built-in tool for viewing the history of actions taken on a Bag: `git reflog show`
1. the Bag can be cloned using any of Git's transport mechanisms, allowing easy duplication and synchronisation of Bags across networks and tracking of workflows using the reflog
1. Git's hooks offer a mechanism for logging to external services, email notifications, etc.

## Disadvantages

Some include:

1. since Git generates SHA1 checksums for all files, SHA1 checksums in BagIt manifests are redundant (but see below)
2. Git operations such as diff are not practical on binary files
3. the size of a GitBag is larger than the equivalent non-Git Bag.

## Are GitBags standard Bags?

Yes. Bags that contain .git directories validate. A GitBag is just a Bag with a .git directory. If you remove the .git directory, the Bag still validates. In this case, having those redundant SHA1 hashes around is good. 

## A example workflow

In this example, I modify the contents of the GitBag's payload (the files in its /data directory). Before I do anything to the GitBag's payload, I clone the GitBag to create a working copy. Then, I update the payload and regnerate the Bag (or update its manifests). Next, I perform a `git commit` on the GitBag. Finally, I replace the original GitBag with the updated working copy. Here are those actions expressed as a series of steps I perform from within the GitBag's directory:

* `git clone mybagdir workingcopy`
* [Edit/modify the payload files]
* [Update the Bag's manifests]
* `commit -am "Did something important to the payload."`
* `mv workingcopy mybagdir`

Later, I use `git log` or `git reflog show` to see the history of actions on the Bag:

```
2215aa5 HEAD@{0}: commit: Did something important to the payload.
3a7b3c0 HEAD@{1}: clone: from /path/to/original/mybagdir/
```

This workflow can easily be scripted. For instance, Python provides libraries for [creating Bags](https://github.com/LibraryOfCongress/bagit-python) and [manipulating Git repositories](https://gitorious.org/git-python).

![This work is in the Public Domain](http://i.creativecommons.org/p/mark/1.0/88x31.png)
